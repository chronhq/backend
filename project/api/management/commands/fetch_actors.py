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

from math import ceil
from datetime import datetime
import re
import requests
from jdcal import gcal2jd
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from api.models import CachedData


def get_date(date_string):
    """
    Parses positive and negative dates and returns as julian date.
    """

    # Positive date
    if not date_string.startswith("-"):

        date = datetime.fromisoformat(date_string[:-1])
        date_jd = (
            ceil(sum(gcal2jd(int(date.year), int(date.month), int(date.day),))) + 0.0
        )
    # Negative date
    else:
        neg_date = re.findall(r"-[\d]+", date_string)
        date_jd = (
            ceil(sum(gcal2jd(int(neg_date[0]), int(neg_date[1]), int(neg_date[2]))))
            + 0.0
        )
    return date_jd


def get_point(actor, point_string):
    """
    Parser the point string value from actor (coorBirth or coorBirth) and
    returns as Point.
    """
    if point_string in actor:
        coords = re.findall(r"[-+]?[\d]+[\.]?\d*", actor[point_string]["value"])
        point = Point(float(coords[0]), float(coords[1]))
    else:
        point = None
    return point


class Command(BaseCommand):
    """
    Populate cached datas with persons.
    """

    help = "Populate cached datas with persons."

    def handle(self, *args, **options):

        url = "https://query.wikidata.org/sparql"
        query = """
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

        r_actors = requests.get(url, params={"format": "json", "query": query})
        actors = r_actors.json()

        statistics_births = {"Created": 0, "Updated": 0, "Current_total": 0}
        statistics_deaths = {"Created": 0, "Updated": 0, "Current_total": 0}

        for actor in actors["results"]["bindings"]:
            # Skip if no name
            if actor["personLabel"]["value"][1:].isdigit():
                print("Skipped {}, no name.".format(actor["personLabel"]["value"]))
                continue

            if "dateOfBirth" in actor and actor["dateOfBirth"]["type"] != "bnode":

                dummy, created = CachedData.objects.update_or_create(
                    event_type=569,
                    wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                    defaults={
                        "location": get_point(actor, "coorBirth"),
                        "date": get_date(actor["dateOfBirth"]["value"]),
                    },
                )
                if created:
                    statistics_births["Created"] += 1
                else:
                    statistics_births["Updated"] += 1
            else:
                print(
                    "Skipped Q{} birth, no birthdate or unknown value".format(
                        actor["person"]["value"].split("Q", 1)[1]
                    )
                )

            if "dateOfDeath" in actor and actor["dateOfDeath"]["type"] != "bnode":

                dummy, created = CachedData.objects.update_or_create(
                    event_type=570,
                    wikidata_id=int(actor["person"]["value"].split("Q", 1)[1]),
                    defaults={
                        "location": get_point(actor, "coorDeath"),
                        "date": get_date(actor["dateOfDeath"]["value"]),
                    },
                )
                if created:
                    statistics_deaths["Created"] += 1
                else:
                    statistics_deaths["Updated"] += 1

            else:
                print(
                    "Skipped Q{} death, doesn't have deathdate or unknown value.".format(
                        actor["person"]["value"].split("Q", 1)[1]
                    )
                )

        statistics_births["Current_total"] = len(
            CachedData.objects.filter(event_type=570)
        )
        statistics_deaths["Current_total"] = len(
            CachedData.objects.filter(event_type=569)
        )
        print("Births:")
        print(statistics_births)
        print("Deaths:")
        print(statistics_deaths)
