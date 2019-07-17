# pylint: disable=C0302

"""
Chron.
Copyright (C) 2019 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
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

from math import ceil
from unittest.mock import patch
from jdcal import gcal2jd
from api.factories import TerritorialEntityFactory

# Response from wikidata
RANK = {
    "outcoming": {"value": "75"},
    "sitelinks": {"value": "185"},
    "incoming": {"value": "65"},
}


# Helpers
def wiki_cd(function):
    """
    Decorator to mock firebase auth
    """

    def wrapper(*args):
        with patch("api.models.CachedData.query_wikidata", return_value=RANK):
            return function(args[0])

    return wrapper


def set_up_data(cls):
    """
  Create basic model instances
  """
    # Constants
    cls.JD_0001 = ceil(sum(gcal2jd(1, 1, 1))) + 0.0
    cls.JD_0002 = ceil(sum(gcal2jd(2, 1, 1))) + 0.0
    cls.JD_0003 = ceil(sum(gcal2jd(3, 1, 1))) + 0.0
    cls.JD_0004 = ceil(sum(gcal2jd(4, 1, 1))) + 0.0
    cls.JD_0005 = ceil(sum(gcal2jd(5, 1, 1))) + 0.0

    # TerritorialEntities
    cls.european_union = TerritorialEntityFactory(
        wikidata_id=10,
        label="European Union",
        color=1,
        admin_level=1,
        inception_date=0,
        dissolution_date=1,
    )
    cls.nato = TerritorialEntityFactory(
        wikidata_id=11,
        label="NATO",
        color=1,
        admin_level=1,
        inception_date=0,
        dissolution_date=1,
    )

    cls.germany = TerritorialEntityFactory(
        wikidata_id=20,
        label="Germany",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )
    cls.france = TerritorialEntityFactory(
        wikidata_id=21,
        label="France",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )
    cls.spain = TerritorialEntityFactory(
        wikidata_id=22,
        label="Spain",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )
    cls.italy = TerritorialEntityFactory(
        wikidata_id=23,
        label="Italy",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )
    cls.british_empire = TerritorialEntityFactory(
        wikidata_id=24,
        label="British Empire",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )
    cls.british_hk = TerritorialEntityFactory(
        wikidata_id=25,
        label="British HK",
        color=1,
        admin_level=2,
        inception_date=0,
        dissolution_date=1,
    )

    cls.alsace = TerritorialEntityFactory(
        wikidata_id=30,
        label="Alsace",
        color=1,
        admin_level=3,
        inception_date=0,
        dissolution_date=1,
    )
    cls.lorraine = TerritorialEntityFactory(
        wikidata_id=31,
        label="Lorraine",
        color=1,
        admin_level=3,
        inception_date=0,
        dissolution_date=1,
    )
