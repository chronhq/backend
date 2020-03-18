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

from requests import get
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ordered_model.models import OrderedModel
from simple_history.models import HistoricalRecords
from colorfield.fields import ColorField


class TileLayout(models.Model):
    """ TileBBox to polygon mapping """

    zoom = models.PositiveIntegerField()
    x_coor = models.PositiveIntegerField()
    y_coor = models.PositiveIntegerField()
    bbox = models.GeometryField()

    class Meta:
        unique_together = ("zoom", "x_coor", "y_coor")


class MVTLayers(models.Model):
    """ Store generated MVT layers """

    zoom = models.PositiveIntegerField()
    x_coor = models.PositiveIntegerField()
    y_coor = models.PositiveIntegerField()
    layer = models.TextField(max_length=64)
    tile = models.BinaryField()

    class Meta:
        unique_together = ("zoom", "x_coor", "y_coor", "layer")


class MapColorScheme(models.Model):
    """ Available Color Palette for STVs """

    color = ColorField(default="#F7F7F7", unique=True)
    palette = models.TextField(max_length=64, blank=True, null=True)
    main = models.BooleanField(default=False, blank=True)


class Vote(models.Model):
    """
    Abstract class to store User's votes
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.BooleanField()

    class Meta:
        abstract = True


class NarrativeVote(Vote):
    """
    Stores votes for Narratives. Extends Vote model
    """

    narrative = models.ForeignKey("Narrative", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("narrative", "user")


class Profile(models.Model):
    """
    Optional profile fields, 1-1 with User instances
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.PointField(blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):  # pylint: disable=W0613
    """
    Creates user profile on post_save for a new User instance
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):  # pylint: disable=W0613
    """
    Saves user profile on post_save for User
    """
    instance.profile.save()


class TerritorialEntity(models.Model):
    """
    A 1-1 mapping between a https://www.wikidata.org/wiki/Q56061, and a PK in our db.
    Holds an additional color information.
    """

    wikidata_id = models.PositiveIntegerField()  # Excluding the Q
    label = models.TextField(max_length=90)
    color = models.ForeignKey(MapColorScheme, on_delete=models.CASCADE)
    admin_level = models.PositiveIntegerField()
    inception_date = models.DecimalField(
        decimal_places=1, max_digits=10, blank=True, null=True
    )
    dissolution_date = models.DecimalField(
        decimal_places=1, max_digits=10, blank=True, null=True
    )

    predecessor = models.ManyToManyField("self", blank=True, symmetrical=False)

    relations = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        through="PoliticalRelation",
        related_name="political_relations",
    )
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if not self.inception_date is None and not self.dissolution_date is None:
            if self.inception_date > self.dissolution_date:
                raise ValidationError(
                    "Inception date cannot be later than dissolution date"
                )

        super(TerritorialEntity, self).clean(*args, **kwargs)

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
    start_date = models.DecimalField(decimal_places=1, max_digits=10)
    end_date = models.DecimalField(decimal_places=1, max_digits=10)

    DIRECT = 10
    INDIRECT = 20
    GROUP = 30
    CONTROL_TYPES = ((DIRECT, "direct"), (INDIRECT, "indirect"), (GROUP, "group"))
    control_type = models.PositiveIntegerField(choices=CONTROL_TYPES)

    user_created = models.BooleanField(default=False)
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
    location = models.PointField(blank=True, null=True)
    date = models.DecimalField(decimal_places=1, max_digits=10)
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

    history = HistoricalRecords()

    def query_wikidata(self):
        """
        Fetch links from wikidata
        """
        url = "https://query.wikidata.org/sparql"
        query = """
        SELECT ?item ?outcoming ?sitelinks ?incoming WHERE {{
            BIND(wd:Q{wid} AS ?item)
            ?item wikibase:statements ?outcoming.
            ?item wikibase:sitelinks ?sitelinks.
            {{
                SELECT (COUNT(?s) AS ?incoming) ?item WHERE {{
                ?s ?p ?item.
                [] wikibase:directClaim ?p.
                }}
                GROUP BY ?item
            }}
        }}
        """.format(
            wid=self.wikidata_id
        )
        req = get(url, params={"format": "json", "query": query})
        return req.json()["results"]["bindings"][0]

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        try:
            data = self.query_wikidata()
            incoming = int(data["incoming"]["value"])
            sitelinks = int(data["sitelinks"]["value"])
            outcoming = int(data["outcoming"]["value"])
            self.rank = incoming + sitelinks + outcoming
        # https://docs.python.org/3/library/json.html#json.JSONDecodeError
        except (IndexError, ValueError):
            self.rank = 0

        super(CachedData, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("wikidata_id", "event_type")


class City(models.Model):
    """
    Stores a city represented by a point on the map
    """

    wikidata_id = models.PositiveIntegerField()  # Excluding the Q
    label = models.TextField(max_length=90)
    location = models.PointField()
    inception_date = models.DecimalField(decimal_places=1, max_digits=10)
    dissolution_date = models.DecimalField(
        decimal_places=1, max_digits=10, blank=True, null=True
    )
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if self.dissolution_date and self.inception_date > self.dissolution_date:
            raise ValidationError(
                "Inception date cannot be later than dissolution date"
            )
        super(City, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(City, self).save(*args, **kwargs)


class SpacetimeVolume(models.Model):
    """
    Maps a set of Territories to a TerritorialEntity at a specific time
    """

    start_date = models.DecimalField(decimal_places=1, max_digits=10)
    end_date = models.DecimalField(decimal_places=1, max_digits=10)
    territory = models.GeometryField()
    entity = models.ForeignKey(
        TerritorialEntity, on_delete=models.CASCADE, related_name="stvs"
    )
    references = ArrayField(models.TextField(max_length=500), blank=True, null=True)
    visual_center = models.PointField(blank=True, null=True)
    related_events = models.ManyToManyField(CachedData, blank=True)
    history = HistoricalRecords()

    def calculate_center(self):
        """
        Calculate and set the visual_center field
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE api_spacetimevolume SET visual_center = foo.visual_center FROM (
                    SELECT *, CASE WHEN ST_Intersects(geom, centroid) IS true
                        THEN centroid ELSE surface END AS visual_center FROM (
                            SELECT id, geom, ST_Centroid(geom)
                            as centroid, ST_PointOnSurface(geom) as surface FROM (
                                SELECT id, geom FROM (
                                    SELECT *,
                                    (MAX(ST_Area(geom)) OVER (PARTITION BY id) = ST_Area(geom))
                                    as sqft
                                    FROM (
                                        SELECT id, (ST_Dump(territory)).geom AS geom
                                        FROM api_spacetimevolume WHERE id = %s
                                    ) as foo
                                ) as foo
                            WHERE sqft = true
                        ) as foo
                    ) as foo
                ) as foo
                WHERE foo.id = api_spacetimevolume.id;
                """,
                [self.pk],
            )

    def clean(self, *args, **kwargs):  # pylint: disable=W0221
        if (
            SpacetimeVolume.objects.filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                entity=self.entity,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                "Another STV for this entity exists in the same timeframe"
            )

        if not self.territory is None:
            if (
                self.territory.geom_type != "Polygon"
                and self.territory.geom_type != "MultiPolygon"
            ):
                raise ValidationError(
                    "Only Polygon and MultiPolygon objects are acceptable geometry types."
                )

        super(SpacetimeVolume, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(SpacetimeVolume, self).save(*args, **kwargs)
        if not self.visual_center:
            self.calculate_center()


class Narrative(models.Model):
    """
    Stores narrative information.
    """

    author = models.TextField(max_length=100)
    title = models.TextField()
    url = models.TextField(unique=True)
    description = models.TextField()
    tags = ArrayField(models.TextField(max_length=100))
    votes = models.ManyToManyField(
        User, related_name="narrative_votes", through=NarrativeVote, blank=True
    )
    history = HistoricalRecords()


class MapSettings(models.Model):
    """
    Stores settings to be used when a narration is active.
    """

    zoom_min = models.FloatField()
    zoom_max = models.FloatField()
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):  # pylint: disable=W0221

        if self.zoom_min < 0.0 or self.zoom_max > 22.0:
            raise ValidationError(
                "Zoom levels should be in the range [0,22] inclusive."
            )

        if self.zoom_min > self.zoom_max:
            raise ValidationError(
                "Minimum zoom level can not be bigger then maximum zoom level."
            )

        super(MapSettings, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.full_clean()
        super(MapSettings, self).save(*args, **kwargs)


class Narration(OrderedModel):
    """
    Each point of narration inside a narrative, commenting on events.
    """

    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    date_label = models.TextField(max_length=100)
    map_datetime = models.DecimalField(decimal_places=2, max_digits=11)
    attached_events = models.ManyToManyField(CachedData, blank=True)
    img = models.URLField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    settings = models.ForeignKey(MapSettings, on_delete=models.CASCADE)
    history = HistoricalRecords()
    location = models.PointField(blank=True, null=True)

    order_with_respect_to = "narrative"


class Symbol(models.Model):
    """
    Stores a FeatureCollection in representation of something
    """

    name = models.TextField(max_length=50)
    narrations = models.ManyToManyField(Narration, related_name="symbols")
    history = HistoricalRecords()


class SymbolFeature(models.Model):
    """
    Stores geometry to be used in a collection in a Symbol
    """

    geom = models.GeometryField()
    styling = HStoreField()
    symbol = models.ForeignKey(
        Symbol, related_name="features", on_delete=models.CASCADE
    )


@receiver(post_save, sender=SpacetimeVolume)
def te_bounds_save(sender, instance, **kwargs):  # pylint: disable=W0613
    """
    When an STV is added or updated, checks it's entities bounding dates
    and changes them if it's needed.
    """
    if (
        instance.entity.inception_date is None
        or instance.entity.inception_date > instance.start_date
    ):
        instance.entity.inception_date = instance.start_date
        instance.entity.save()
    if (
        instance.entity.dissolution_date is None
        or instance.entity.dissolution_date < instance.end_date
    ):
        instance.entity.dissolution_date = instance.end_date
        instance.entity.save()


@receiver(post_delete, sender=SpacetimeVolume)
def te_bounds_delete(sender, instance, **kwargs):  # pylint: disable=W0613
    """
    When an STV is deleted, checks if the entity was using it as it's bouding dates and finds the
    new date if that's the case.
    """
    if (
        instance.entity.inception_date is not None
        and instance.entity.inception_date == instance.start_date
    ):
        start = SpacetimeVolume.objects.filter(entity=instance.entity).order_by(
            "start_date"
        )
        if len(start) != 0:
            instance.entity.inception_date = start[0].start_date
        else:
            instance.entity.inception_date = None
        instance.entity.save()
    if (
        instance.entity.dissolution_date is not None
        and instance.entity.dissolution_date == instance.end_date
    ):
        end = SpacetimeVolume.objects.filter(entity=instance.entity).order_by(
            "-end_date"
        )
        if len(end) != 0:
            instance.entity.dissolution_date = end[0].end_date
        else:
            instance.entity.dissolution_date = None
        instance.entity.save()
