"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O'Flynn, Mikhail Orlov.

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
    help = 'Populate cached datas with treaties.'


    def handle(self, *args, **options):
        URL = "https://query.wikidata.org/sparql"
        QUERY = """
        SELECT ?treaty ?treatyLabel ?time ?location ?coors
        WHERE
        {
        ?treaty wdt:P31 wd:Q625298.
        ?treaty wdt:P585 ?time.
        OPTIONAL {
            ?treaty wdt:P276 ?location.
            ?location wdt:P625 ?coors
        }
        FILTER (?time > "1700-01-01T00:00:00Z"^^xsd:dateTime)
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        }
        """
        R_TREATIES = requests.get(URL, params={"format": "json", "query": QUERY})
        TREATIES = R_TREATIES.json()

        statistics = {"Created": 0, "Updated": 0, "Current_total": 0}

        for treaty in TREATIES["results"]["bindings"]:
            if treaty["treatyLabel"]["value"][1:].isdigit():
                print("Skipped {}, no name.".format(treaty['treatyLabel']['value']))
                continue

            if "time" in treaty and treaty["time"]["type"] != "bnode":
                treaty_date = datetime.fromisoformat(treaty["time"]["value"][:-1])
            else:
                print("Skipped Q{}, no date or unknown date.".format(treaty['treatyLabel']['value'].split('Q', 1)[1]))
                continue
            
            if "coors" in treaty and treaty["coors"]["type"] != "bnode":
                coords = re.findall(r'[-+]?[\d]+[\.]?\d*',treaty["coors"]["value"])
                point = Point(float(coords[0]), float(coords[1]))
            else:
                point = None


            data, created = CachedData.objects.update_or_create(event_type=131569, 
                                                            wikidata_id=int(treaty["treaty"]["value"].split("Q", 1)[1]),
                                                            defaults={'location': point, 'date' :ceil(sum(gcal2jd(int(treaty_date.year), int(treaty_date.month), int(treaty_date.day)))) + 0.0})

            if created:
                statistics["Created"] += 1
            else:
                statistics["Updated"] += 1


            
        statistics["Current_total"] = len(CachedData.objects.filter(event_type=178561))

        print(statistics)