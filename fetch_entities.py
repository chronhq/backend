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
SELECT ?entity ?predecessors
WHERE
{
	VALUES ?countryclass { wd:Q3024240 wd:Q6256 }
  	?entity wdt:P31 ?countryclass ;
	   wdt:P571 ?inception .
	OPTIONAL { ?entity wdt:P576 ?dissolved } .
    OPTIONAL { ?entity wdt:P155 ?predecessors } .
	FILTER (?inception < "1815-01-01T00:00:00Z"^^xsd:dateTime) 
	FILTER (?dissolved >= "1789-01-01T00:00:00Z"^^xsd:dateTime || !Bound(?dissolved) )
	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
"""
R_ENTITIES = requests.get(URL, params={"format": "json", "query": QUERY})
ENTITIES = R_ENTITIES.json()

for entity in ENTITIES["results"]["bindings"]:
    data = {
        "wikidata_id": int(entity["entity"]["value"].split("Q", 1)[1]),
        "color": "#fff", # TODO: change
        "admin_level": 1,
        "predecessors": [] # entity["predecessors"]["value"]
    }
    r_te = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/territorial-entities/",
        data,
        params={"format": "json"},
    )
    print(str(r_te.status_code) + ": " + r_te.reason)
