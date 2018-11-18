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

from django.db import models
from polymorphic.models import PolymorphicModel

# Create your models here.
class PoliticalEntity(models.Model):
    """
    A 1-1 mapping between a https://www.wikidata.org/wiki/Q56061, and a PK in our db.
    Holds an additional color information.
    """

    wikidata_id = models.IntegerField()  # Excluding the Q
    color = models.IntegerField()
    admin_level = models.IntegerField()
    predecessor = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )


class PoliticalRelation(PolymorphicModel):
    """
    Abstract class for various political relations
    """

    start_date = models.DateField()
    end_date = models.DateField()


class DirectPoliticalRelation(PoliticalRelation):
    """
    Contains administrative territorial entity:
        https://www.wikidata.org/wiki/Property:P150
    and its reverse:
        https://www.wikidata.org/wiki/Property:P131
    """

    parent = models.ForeignKey(PoliticalEntity, on_delete=models.CASCADE)
    child = models.ForeignKey(PoliticalEntity, on_delete=models.CASCADE)


class IndirectPoliticalRelation(PoliticalRelation):
    """
    Dependant territory and client state
        https://www.wikidata.org/wiki/Q161243
        https://www.wikidata.org/wiki/Q1151405
    """

    parent = models.ForeignKey(PoliticalEntity, on_delete=models.CASCADE)
    child = models.ForeignKey(PoliticalEntity, on_delete=models.CASCADE)
    relation_type = (
        models.IntegerField()
    )  # Wikidata ID of relation type, excluding the Q
