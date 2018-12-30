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
SELECT ?battle ?coordinate_location ?point_in_time WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?battle wdt:P31 wd:Q178561.
  ?battle wdt:P361 wd:Q78994.
  ?battle wdt:P625 ?coordinate_location.
  ?battle wdt:P585 ?point_in_time.
}
"""
R_BATTLES = requests.get(URL, params={"format": "json", "query": QUERY})
BATTLES = R_BATTLES.json()

for battle in BATTLES["results"]["bindings"]:
    data = {
        "event_type": 178561,
        "wikidata_id": int(battle["battle"]["value"].split("Q", 1)[1]),
        "location": battle["coordinate_location"]["value"],
        "date": datetime.strptime(
            battle["point_in_time"]["value"][:-1], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%Y-%m-%d"),
    }
    r_battle = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
        data,
        params={"format": "json"},
    )
    print(str(r_battle.status_code) + ": " + r_battle.reason)
