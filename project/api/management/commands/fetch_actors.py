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
    help = 'Populate cached datas with persons.'


    def handle(self, *args, **options):

        URL = "https://query.wikidata.org/sparql"
        QUERY = """
        SELECT ?person ?personLabel ?dateOfBirth ?dateOfDeath ?placeOfBirth ?placeOfDeath ?coorBirth ?coorDeath ?occupation WHERE {
        ?person wdt:P31 wd:Q5.
        OPTIONAL {
            ?person wdt:P569 ?dateOfBirth.
            ?person wdt:P19 ?placeOfBirth.
            ?placeOfBirth wdt:P625 ?coorBirth.
            FILTER(?dateOfBirth > "1700-01-01T00:00:00Z"^^xsd:dateTime)
        }
        OPTIONAL {
            ?person wdt:P570 ?dateOfDeath.
            ?person wdt:P20 ?placeOfDeath.
            ?placeOfDeath wdt:P625 ?coorDeath.
        }
        ?person wdt:P106 ?occupation.
        FILTER(?occupation IN(wd:Q116, wd:Q30461, wd:Q1097498, wd:Q372436))
        FILTER(?dateOfBirth > "1700-01-01T00:00:00Z"^^xsd:dateTime || ?dateOfDeath > "1700-01-01T00:00:00Z"^^xsd:dateTime)
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        """

        R_ACTORS = requests.get(URL, params={"format": "json", "query": QUERY})
        ACTORS = R_ACTORS.json()

        statistics_births = {"Created": 0, "Updated": 0, "Current_total": 0}
        statistics_deaths = {"Created": 0, "Updated": 0, "Current_total": 0}

        for actor in ACTORS["results"]["bindings"]:
            if actor["personLabel"]["value"][1:].isdigit():
                print(f"Skipped {actor['personLabel']['value']}, no name.")
                continue

            try:
                if actor["dateOfBirth"]["type"] == 'bnode':
                    print(f"Skipped Q{actor['person']['value'].split('Q', 1)[1]}, birthdate unknown value")
                    continue
                birth_date = datetime.fromisoformat(actor["dateOfBirth"]["value"][:-1])
              
                if "coorBirth" in actor:
                    coords = re.findall(r'[-+]?[\d]+[\.]?\d*',actor["coorBirth"]["value"])
                    point = Point(float(coords[0]), float(coords[1]))
                else:
                    point = None


                data, created = CachedData.objects.update_or_create(event_type=569, 
                                                                wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                                                                defaults={'location': point, 'date' : ceil(sum(gcal2jd(int(birth_date.year), int(birth_date.month), int(birth_date.day)))) + 0.0})
                if created:
                    statistics_births["Created"] += 1
                else:
                    statistics_births["Updated"] += 1

            except KeyError:
                print(f"Skipped Q{actor['person']['value'].split('Q', 1)[1]}, doesn't have birthdate")

            try:
                if actor["dateOfDeath"]["type"] == 'bnode':
                    print(f"Skipped Q{actor['person']['value'].split('Q', 1)[1]} deathdate, unknown value")
                    continue

                death_date = datetime.fromisoformat(actor["dateOfDeath"]["value"][:-1])
              
                if "coorDeath" in actor:
                    coords = re.findall(r'[-+]?[\d]+[\.]?\d*',actor["coorDeath"]["value"])
                    point = Point(float(coords[0]), float(coords[1]))
                else:
                    point = None

                data, created = CachedData.objects.update_or_create(event_type=570, 
                                                                wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                                                                defaults={'location': point, 'date' : ceil(sum(gcal2jd(int(death_date.year), int(death_date.month), int(death_date.day)))) + 0.0})
                if created:
                    statistics_deaths["Created"] += 1
                else:
                    statistics_deaths["Updated"] += 1
                
            except KeyError:
                print(f"Skipped Q{actor['person']['value'].split('Q', 1)[1]}, doesn't have deathdate")


        statistics_births["Current_total"] = len(CachedData.objects.filter(event_type=570))
        statistics_deaths["Current_total"] = len(CachedData.objects.filter(event_type=569))
        print("Births:")
        print(statistics_births)
        print("Deaths:")
        print(statistics_deaths)

