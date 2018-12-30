"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from random import randint
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from colorfield.fields import ColorField
from simple_history.models import HistoricalRecords


class TerritorialEntity(models.Model):
    """
    A 1-1 mapping between a https://www.wikidata.org/wiki/Q56061, and a PK in our db.
    Holds an additional color information.
    """

    wikidata_id = models.PositiveIntegerField(primary_key=True)  # Excluding the Q
    color = ColorField()
    admin_level = models.PositiveIntegerField()
    predecessors = models.ManyToManyField("self", blank=True, related_name="successors")
    relations = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        through="PoliticalRelation",
        related_name="political_relations",
    )

    history = HistoricalRecords()

    def get_children(self):
        """
        Returns relations in which this nation is a parent
        """
        return self.relations

    def get_parents(self):
        """
        Returns relations in which this nation is a child
        """
        return self.political_relations  # pylint: disable=E1101


class PoliticalRelation(models.Model):
    """
    Stores various political relations
    """

    parent = models.ForeignKey(
        TerritorialEntity, related_name="children", on_delete=models.CASCADE
    )
    child = models.ForeignKey(
        TerritorialEntity, related_name="parents", on_delete=models.CASCADE
    )

    start_date = models.DateField()
    end_date = models.DateField()

    DIRECT = 10
    DIRECT_OCCUPED = 11
    DIRECT_DISPUTED = 12
    INDIRECT = 20
    INDIRECT_DISPUTED = 21
    GROUP = 30
    CONTROL_TYPES = (
        (DIRECT, "direct"),
        (DIRECT_OCCUPED, "direct_occupied"),
        (DIRECT_DISPUTED, "direct_disputed"),
        (INDIRECT, "indirect"),
        (INDIRECT_DISPUTED, "indirect_disputed"),
        (GROUP, "group"),
    )
    control_type = models.PositiveIntegerField(choices=CONTROL_TYPES)

    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")

        if self.child.admin_level < self.parent.admin_level:
            raise ValidationError(
                "Child entity's admin level cannot be less than parent entity's"
            )

        super(PoliticalRelation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(PoliticalRelation, self).save(*args, **kwargs)


class CachedData(models.Model):
    """
    Stores cache of ranked Wikidata entities
    """

    wikidata_id = models.PositiveIntegerField()  # Excluding the Q
    location = models.PointField()
    date = models.DateField()
    rank = models.PositiveIntegerField()

    BATTLE = 178561
    DOCUMENT = 131569
    BIRTH = 569
    DEATH = 570
    EVENT_TYPES = (
        (BATTLE, "battle"),
        (DOCUMENT, "document"),
        (BIRTH, "birth"),
        (DEATH, "death"),
    )
    event_type = models.PositiveIntegerField(choices=EVENT_TYPES)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.rank = self.wikidata_id * randint(0, 10)  # TODO: implement #8
        super(CachedData, self).save(*args, **kwargs)


class AtomicPolygon(models.Model):
    """
    Stores geometric data corresponding to a wikidata ID
    """

    wikidata_id = models.PositiveIntegerField(
        unique=True, blank=True, null=True
    )  # Excluding the Q
    name = models.TextField(max_length=100, unique=True)
    geom = models.GeometryField()

    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if not self.geom is None:
            if (
                self.geom.geom_type != "Polygon"
                and self.geom.geom_type != "MultiPolygon"
            ):
                raise ValidationError(
                    "Only Polygon and MultiPolygon objects are acceptable geometry types."
                )

            if (
                AtomicPolygon.objects.filter(geom__intersects=self.geom)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    "Another AtomicPolygon overlaps this polygon: "
                    + "\n".join(
                        str(i)
                        for i in AtomicPolygon.objects.filter(
                            geom__intersects=self.geom
                        )
                    )
                )

        super(AtomicPolygon, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(AtomicPolygon, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SpacetimeVolume(models.Model):
    """
    Maps a set of AtomicPolygons to a TerritorialEntity at a specific time
    """

    start_date = models.DateField()
    end_date = models.DateField()
    territory = models.ManyToManyField(AtomicPolygon)
    entity = models.ForeignKey(TerritorialEntity, on_delete=models.CASCADE)
    references = ArrayField(models.TextField(max_length=500))
    # related_events = models.ManyToManyField(Event)
    # TODO: implement Event model

    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if (
            SpacetimeVolume.objects.filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                entity__exact=self.entity,
            )
            .exclude(pk__exact=self.pk)
            .exists()
        ):
            raise ValidationError(
                "Another STV for this entity exists in the same timeframe"
            )
        super(SpacetimeVolume, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(SpacetimeVolume, self).save(*args, **kwargs)
