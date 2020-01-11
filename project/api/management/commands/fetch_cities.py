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
import re
from datetime import datetime
from math import ceil
import requests
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from jdcal import gcal2jd
from api.models import City


def get_point(city):
    """
    Parses coordinates and returns as Point.
    """
    # Location in city and not blank
    if "location" in city and city["location"]["type"] != "bnode":
        coords = re.findall(r"[-+]?[\d]+[\.]?\d*", city["location"]["value"])
        point = Point(float(coords[0]), float(coords[1]))
    else:
        point = None
    return point


def get_date(date_string):
    """
    Parses positive and negative dates and returns as julian date.
    """

    # Positive date
    if not date_string.startswith("-"):

        date = datetime.fromisoformat(date_string[:-1])
        jd_date = (
            ceil(sum(gcal2jd(int(date.year), int(date.month), int(date.day),))) + 0.0
        )
    # Negative date
    else:
        date = re.findall(r"-[\d]+", date_string)
        jd_date = ceil(sum(gcal2jd(int(date[0]), int(date[1]), int(date[2])))) + 0.0
    return jd_date


class Command(BaseCommand):
    """
    Populate cached datas with cities.
    """

    help = "Populate cached datas with cities."

    def handle(self, *args, **options):
        url = "https://query.wikidata.org/sparql"
        query = """
        SELECT DISTINCT ?city ?cityLabel ?inception (SAMPLE(?location) AS ?location) ?dissolution WHERE {
        ?country wdt:P31 wd:Q3624078 .
        ?country wdt:P36 ?city.
        ?city wdt:P625 ?location.
        OPTIONAL { ?city wdt:P571 ?inception. }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        OPTIONAL { ?city wdt:P576 ?dissolution. }
        }
        GROUP BY ?city ?cityLabel ?inception ?dissolution
        """
        r_cities = requests.get(url, params={"format": "json", "query": query})
        cities = r_cities.json()

        statistics = {"Created": 0, "Updated": 0, "Current_total": 0}

        for city in cities["results"]["bindings"]:
            if city["cityLabel"]["value"][1:].isdigit():
                print("Skipped {}".format(city["cityLabel"]["value"]))
                continue

            # Inception exists and not unknown/no value
            if "inception" in city and city["inception"]["type"] != "bnode":

                inception = get_date(city["inception"]["value"])

            else:
                print(
                    "Skipped Q{}, no inception date or unknown value.".format(
                        city["city"]["value"].split("Q", 1)[1]
                    )
                )
                continue

            # Dissolution exists and not unknown/no value
            if "dissolution" in city and city["dissolution"]["type"] != "bnode":
                dissolution_value = city["dissolution"]["value"]

                # Positive date
                if not dissolution_value.startswith("-"):

                    dissolution = get_date(city["inception"]["value"])

            else:
                # Don't skip since the city might still exist if no dissolution date
                dissolution = None

            dummy, created = City.objects.update_or_create(
                wikidata_id=int(city["city"]["value"].split("Q", 1)[1]),
                defaults={
                    "location": get_point(city),
                    "label": city["cityLabel"]["value"],
                    "inception_date": inception,
                    "dissolution_date": dissolution,
                },
            )

            if created:
                statistics["Created"] += 1
            else:
                statistics["Updated"] += 1

        statistics["Current_total"] = len(City.objects.filter())
        print(statistics)
