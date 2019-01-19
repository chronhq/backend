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

from datetime import datetime
import requests
import os

URL = "https://query.wikidata.org/sparql"
QUERY = """
SELECT DISTINCT ?city ?cityLabel ?inception (SAMPLE(?location) AS ?location) ?dissolution WHERE {
  ?city (wdt:P31/wdt:P279*) wd:Q515.
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
    data = {
        "wikidata_id": int(city["city"]["value"].split("Q", 1)[1]),
        "label": city["cityLabel"]["value"],
        "location": city["location"]["value"],
        "inception_date": datetime.strptime(
            city["inception"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%Y-%m-%d") if "inception" in city else "0001-01-01",
        "dissolution_date": datetime.strptime(
            city["dissolution"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%Y-%m-%d") if "dissolution" in city else "",
    }
    r_city = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cities/",
        data,
        params={"format": "json"},
    )
    print(str(r_city.status_code) + ": " + r_city.reason)
