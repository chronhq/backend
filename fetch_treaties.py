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
import requests
import os

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
  FILTER (?time > "1789-01-01T00:00:00Z"^^xsd:dateTime)
  FILTER (?time < "1816-01-01T00:00:00Z"^^xsd:dateTime)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
"""
R_TREATIES = requests.get(URL, params={"format": "json", "query": QUERY})
TREATIES = R_TREATIES.json()

for treaty in TREATIES["results"]["bindings"]:
    if treaty["treatyLabel"]["value"][1:].isdigit():
        print(f"Skipped {treaty['treatyLabel']['value']}")
        continue

    data = {
        "event_type": 131_569,
        "wikidata_id": int(treaty["treaty"]["value"].split("Q", 1)[1]),
        "location": treaty["coors"]["value"] if "coors" in treaty else None,
        "date": datetime.strptime(
            treaty["time"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%Y-%m-%d"),
    }
    r_treaty = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
        data,
        params={"format": "json"},
    )
    print(str(r_treaty.status_code) + ": " + r_treaty.reason)
