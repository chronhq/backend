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
from api.models import City
from datetime import datetime
from jdcal import gcal2jd
from math import ceil
import re
import os
import requests


class Command(BaseCommand):
    help = 'Populate cached datas with cities.'


    def handle(self, *args, **options):
        URL = "https://query.wikidata.org/sparql"
        QUERY = """
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
        R_CITIES = requests.get(URL, params={"format": "json", "query": QUERY})
        CITIES = R_CITIES.json()

        for city in CITIES["results"]["bindings"]:
            if city["cityLabel"]["value"][1:].isdigit():
                print(f"Skipped {city['cityLabel']['value']}")
                continue


            # Inception exists and not unknown/no value
            if "inception" in city and city["inception"]["type"] != "bnode":
                inception_value = city["inception"]["value"]

                # Positive date
                if not inception_value.startswith("-"):

                    inception = datetime.fromisoformat(inception_value[:-1])
                    inception_date = ceil(sum(gcal2jd(int(inception.year), int(inception.month), int(inception.day)))) + 0.0
                # Negative date
                else:
                    neg_date = re.findall(r'-[\d]+', inception_value)
                    inception_date = gcal2jd(int(neg_date[0]), int(neg_date[1]), int(neg_date[2])) 
            else:
                inception_date = None

            # Dissolution exists and not unknown/no value
            if "dissolution" in city and city["dissolution"]["type"] != "bnode":
                dissolution_value = city["dissolution"]["value"]

                # Positive date
                if not dissolution_value.startswith("-"):

                    dissolution = datetime.fromisoformat(dissolution_value[:-1])
                    dissolution_date = ceil(sum(gcal2jd(int(dissolution.year), int(dissolution.month), int(dissolution.day)))) + 0.0
                
                # Negative date
                else:
                    neg_date = re.findall(r'-[\d]+', dissolution_value)
                    dissolution_date = gcal2jd(int(neg_date[0]), int(neg_date[1]), int(neg_date[2])) 
            else:
                dissolution_date = None

            # Location in city and not blank 
            if "location" in city and city["location"]["type"] != "bnode":
                coords = re.findall(r'[-+]?[\d]+[\.]?\d*',city["location"]["value"])
                point = Point(float(coords[0]), float(coords[1]))
            else:
                point = None


            new_city = City(wikidata_id=int(city["city"]["value"].split("Q", 1)[1]),
                label=city["cityLabel"]["value"],
                location=point,
                inception_date=inception_date,
                dissolution_date=dissolution_date
            )
