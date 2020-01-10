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
            # Skip if no name
            if actor["personLabel"]["value"][1:].isdigit():
                print(f"Skipped {actor['personLabel']['value']}, no name.")
                continue

            
            if "dateOfBirth" in actor and actor["dateOfBirth"]["type"] != 'bnode':

                birth_value = actor["dateOfBirth"]["value"]
                # Positive date
                if not birth_value.startswith("-"):

                    birth_datetime = datetime.fromisoformat(birth_value[:-1])
                    birth_date = ceil(sum(gcal2jd(int(birth_datetime.year), int(birth_datetime.month), int(birth_datetime.day)))) + 0.0
                # Negative date
                else:
                    neg_date = re.findall(r'-[\d]+', birth_value)
                    birth_date = ceil(sum(gcal2jd(int(neg_date[0]), int(neg_date[1]), int(neg_date[2])))) + 0.0
              
                if "coorBirth" in actor:
                    coords = re.findall(r'[-+]?[\d]+[\.]?\d*',actor["coorBirth"]["value"])
                    point = Point(float(coords[0]), float(coords[1]))
                else:
                    point = None


                data, created = CachedData.objects.update_or_create(event_type=569, 
                                                                wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                                                                defaults={'location': point, 'date' : birth_date})
                if created:
                    statistics_births["Created"] += 1
                else:
                    statistics_births["Updated"] += 1
            else:
                print("Skipped Q{} birth, no birthdate or unknown value".format(actor['person']['value'].split('Q', 1)[1]))

            if "dateOfDeath" in actor and actor["dateOfDeath"]["type"] != 'bnode':

                death_value = actor["dateOfDeath"]["value"]
                # Positive date
                if not birth_value.startswith("-"):

                    death_datetime = datetime.fromisoformat(death_value[:-1])
                    death_date = ceil(sum(gcal2jd(int(death_datetime.year), int(death_datetime.month), int(death_datetime.day)))) + 0.0
                # Negative date
                else:
                    neg_date = re.findall(r'-[\d]+', death_value)
                    death_date = ceil(sum(gcal2jd(int(neg_date[0]), int(neg_date[1]), int(neg_date[2])))) + 0.0
              
                if "coorDeath" in actor:
                    coords = re.findall(r'[-+]?[\d]+[\.]?\d*',actor["coorDeath"]["value"])
                    point = Point(float(coords[0]), float(coords[1]))
                else:
                    point = None

                data, created = CachedData.objects.update_or_create(event_type=570, 
                                                                wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                                                                defaults={'location': point, 'date' : death_date})
                if created:
                    statistics_deaths["Created"] += 1
                else:
                    statistics_deaths["Updated"] += 1
                
            else:
                print(f"Skipped Q{actor['person']['value'].split('Q', 1)[1]} death, doesn't have deathdate or unknown value")


        statistics_births["Current_total"] = len(CachedData.objects.filter(event_type=570))
        statistics_deaths["Current_total"] = len(CachedData.objects.filter(event_type=569))
        print("Births:")
        print(statistics_births)
        print("Deaths:")
        print(statistics_deaths)

