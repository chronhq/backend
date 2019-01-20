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
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?parent ?parentLabel ?child ?childLabel ?inception ?dissolved WHERE {
  VALUES (?countryclass) {
    (wd:Q3024240)
    (wd:Q6256)
  }
  ?parent wdt:P31 ?countryclass.
  ?parent wdt:P150* ?child.
  ?parent wdt:P571 ?inception.
  OPTIONAL { ?parent wdt:P576 ?dissolved. }
  FILTER(?inception < "1815-01-01T00:00:00Z"^^xsd:dateTime)
  FILTER((?dissolved >= "1789-01-01T00:00:00Z"^^xsd:dateTime) || (!BOUND(?dissolved)))
  FILTER(?parent != ?child)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
"""
R_DPRS = requests.get(URL, params={"format": "json", "query": QUERY})
DPRS = R_DPRS.json()

for dpr in DPRS["results"]["bindings"]:
    try:
        data = {
            "control_type": 10,  # direct
            "parent": int(dpr["parent"]["value"].split("Q", 1)[1]),
            "child": int(dpr["child"]["value"].split("Q", 1)[1]),
            "start_date": datetime.strptime(
                dpr["inception"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d"),
            "end_date": datetime.strptime(
                dpr["dissolved"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d"),
        }
        r_dpr = requests.post(
            os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
            data,
            params={"format": "json"},
        )
        print(str(r_dpr.status_code) + ": " + r_dpr.reason)
    except KeyError:
        print("No coordiantes for " + dpr["dprLabel"]["value"])
