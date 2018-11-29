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

from django.core.exceptions import ValidationError
from django.db import models
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
        related_name="related_to",
    )

    history = HistoricalRecords()

    def get_children(self):
        return self.relations

    def get_parents(self):
        return self.related_to


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

        super(PoliticalRelation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(PoliticalRelation, self).save(*args, **kwargs)
