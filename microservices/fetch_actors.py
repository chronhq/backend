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
import os
import requests

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

for actor in ACTORS["results"]["bindings"]:
    if actor["personLabel"]["value"][1:].isdigit():
        print(f"Skipped {actor['personLabel']['value']}")
        continue

    try:
        birth_data = {
            "event_type": 569,
            "wikidata_id": int(actor["person"]["value"].split("Q", 1)[1]),
            "location": actor["coorBirth"]["value"] if "coorBirth" in actor else None,
            "date": datetime.strptime(
                actor["dateOfBirth"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d"),
        }
        r_birth = requests.post(
            os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
            birth_data,
            params={"format": "json"},
        )
        print("Birth: " + str(r_birth.status_code) + ": " + r_birth.reason)
    except KeyError:
        print("Birth: unknown")

    try:
        death_data = {
            "event_type": 570,
            "wikidata_id": int(actor["person"]["value"].split("Q", 1)[1]),
            "location": actor["coorDeath"]["value"] if "coorDeath" in actor else None,
            "date": datetime.strptime(
                actor["dateOfDeath"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d"),
        }
        r_death = requests.post(
            os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
            death_data,
            params={"format": "json"},
        )
        print("Death: " + str(r_death.status_code) + ": " + r_death.reason)
    except KeyError:
        print("Death: unknown")
