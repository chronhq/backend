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

from datetime import datetime
import os
import requests

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

    inception = "0001-01-01"
    if "inception" in city and not city["inception"]["value"].startswith("-"):
        inception = city["inception"]["value"]

        # date parsing
        year = inception.split("-")[0]
        if len(year) < 4:
            inception = "0" * (4 - len(year)) + year + "-" + inception.split("-", 1)[1]

        if inception.startswith("t"):
            inception = datetime.fromtimestamp(int(inception[1:])).strftime("%Y-%m-%d")
        else:
            inception = datetime.strptime(inception[:-1], "%Y-%m-%dT%H:%M:%S").strftime(
                "%Y-%m-%d"
            )

        year = inception.split("-")[0]
        if len(year) < 4:
            inception = "0" * (4 - len(year)) + year + "-" + inception.split("-", 1)[1]

    dissolution = None
    if "dissolution" in city and not city["dissolution"]["value"].startswith("-"):
        dissolution = city["dissolution"]["value"]

        # date parsing
        year = dissolution.split("-")[0]
        if len(year) < 4:
            dissolution = (
                "0" * (4 - len(year)) + year + "-" + dissolution.split("-", 1)[1]
            )

        if dissolution.startswith("t"):
            dissolution = datetime.fromtimestamp(int(dissolution[1:])).strftime(
                "%Y-%m-%d"
            )
        else:
            dissolution = datetime.strptime(
                dissolution[:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d")

        year = dissolution.split("-")[0]
        if len(year) < 4:
            dissolution = (
                "0" * (4 - len(year)) + year + "-" + dissolution.split("-", 1)[1]
            )

    data = {
        "wikidata_id": int(city["city"]["value"].split("Q", 1)[1]),
        "label": city["cityLabel"]["value"],
        "location": city["location"]["value"],
        "inception_date": inception,
        "dissolution_date": dissolution,
    }
    r_city = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cities/",
        data,
        params={"format": "json"},
    )
    print(str(r_city.status_code) + ": " + r_city.reason)

    if r_city.status_code != 201:
        print(data)
        print(r_city.json())
