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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from api.models import CachedData
from datetime import datetime
from jdcal import gcal2jd
from math import ceil
import re
import os
import requests

class Command(BaseCommand):
    help = 'Populate cached datas with battles.'


    def handle(self, *args, **options):

        URL = "https://query.wikidata.org/sparql"
        QUERY = """
        SELECT ?battle ?battleLabel ?point_in_time ?coordinate_location WHERE {
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        ?battle (wdt:P31/wdt:P279*) wd:Q178561.
        ?battle wdt:P585 ?point_in_time.
        FILTER(?point_in_time >= "1700-01-01T00:00:00Z"^^xsd:dateTime)
        OPTIONAL { ?battle wdt:P625 ?coordinate_location. }
        }
        """
        R_BATTLES = requests.get(URL, params={"format": "json", "query": QUERY})
        BATTLES = R_BATTLES.json()

        statistics = {"Created": 0, "Updated": 0, "Current_total": 0}
        for battle in BATTLES["results"]["bindings"]:
           
            if "point_in_time" in battle and battle["point_in_time"]["type"] != "bnode":
                battle_date = datetime.fromisoformat(battle["point_in_time"]["value"][:-1])
            else:
                print("Skipped Q{}, no date or unknown value".format(battle['battle']['value'].split('Q', 1)[1]))
                continue


            if "coordinate_location" in battle and battle["coordinate_location"]["type"] != "bnode":
                coords = re.findall(r'[-+]?[\d]+[\.]?\d*',battle["coordinate_location"]["value"])
                point = Point(float(coords[0]), float(coords[1]))
            else:
                point = None


            data, created = CachedData.objects.update_or_create(event_type=178561, 
                                                                wikidata_id=int(battle["battle"]["value"].split("Q", 1)[1]),
                                                                defaults={'location': point, 'date' : ceil(sum(gcal2jd(int(battle_date.year), int(battle_date.month), int(battle_date.day)))) + 0.0})

            if created:
                statistics["Created"] += 1
            else:
                statistics["Updated"] += 1

        statistics["Current_total"] = len(CachedData.objects.filter(event_type=178561))

        print(statistics)