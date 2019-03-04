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
import csv
import re
import requests


def populate_cd(wid, is_battle):
    """
    Populates CachedData table for missing values
    Returns: ID for new item
    """
    cd_url = "https://query.wikidata.org/sparql"
    cd_query = """
    SELECT ?event ?start_time ?point_in_time ?coors
    WHERE
    {{
        BIND(wd:Q{} as ?event)
        ?event wdt:P276 ?location.
        ?location wdt:P625 ?coors
        OPTIONAL {{ ?event wdt:P580 ?start_time. }}
        OPTIONAL {{ ?event wdt:P585 ?point_in_time. }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    """.format(
        wid
    )
    event_info = requests.get(
        cd_url, params={"format": "json", "query": cd_query}
    ).json()["results"]["bindings"]
    if event_info and (
        "start_time" in event_info[0] or "point_in_time" in event_info[0]
    ):
        event_info = event_info[0]
    else:
        return None
    cd_date = datetime.strptime(
        event_info["point_in_time"]["value"][:-1]
        if "point_in_time" in event_info
        else event_info["start_time"]["value"][:-1],
        "%Y-%m-%dT%H:%M:%S",
    ).strftime("%Y-%m-%d")
    cd_data = {
        "event_type": 178_561 if is_battle else 131_569,
        "wikidata_id": wid,
        "location": event_info["coors"]["value"],
        "date": cd_date,
    }
    new_cd = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
        cd_data,
        params={"format": "json"},
    )
    return int(new_cd.json()["id"])


NARRATIVE_DATA = {
    "author": "Bamber Gascoigne <http://www.historyworld.net>",
    "title": "Napoleonic Wars",
    "description": "History of the Napoleonic Wars",
    "tags": [
        "military",
        "conflict",
        "france",
        "europe",
        "revolution",
        "napoleon",
        "late modern era",
    ],
    "url": "napoleon",
}
R_NARRATIVE = requests.post(
    os.getenv("API_ROOT", "http://localhost/api/") + "/narratives/",
    NARRATIVE_DATA,
    params={"format": "json"},
)
NARRATIVE_ID = R_NARRATIVE.json()["id"]
print(
    "Narrative #{}// {}: {}".format(
        NARRATIVE_ID, str(R_NARRATIVE.status_code), R_NARRATIVE.reason
    )
)

with open("data.csv", mode="r") as narrative_file:
    NARRATIVE_READER = csv.DictReader(narrative_file)
    for row in NARRATIVE_READER:
        # TODO: fix placeholder MapSettings
        ms_data = {
            "bbox": "MULTIPOINT(-15.751 35.382, 51.046 62.222)",
            "zoom_min": 1,
            "zoom_max": 15,
        }
        r_ms = requests.post(
            os.getenv("API_ROOT", "http://localhost/api/") + "/map-settings/",
            ms_data,
            params={"format": "json"},
        )
        ms_id = r_ms.json()["id"]
        print(
            "MapSettings #{}// {}: {}".format(ms_id, str(r_ms.status_code), r_ms.reason)
        )

        first_year = row["year"].split("-")[0] if "-" in row["year"] else row["year"]
        first_year_dt = datetime.strptime(first_year, "%Y").isoformat()
        battle_events = []
        treaty_events = []
        for battle in row["battles"].splitlines():
            URL = "https://query.wikidata.org/sparql"
            QUERY = """
                SELECT DISTINCT ?battle ?battleLabel WHERE {{
                    hint:Query hint:optimizer "None".
                    VALUES (?type) {{
                        (wd:Q178561)
                        (wd:Q188055)
                    }}
                    ?subtype wdt:P279* ?type.
                    ?battle wdt:P31 ?subtype.
                    ?battle rdfs:label ?queryByTitle.
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    FILTER(REGEX(?queryByTitle, "{}", "i"))
                }}
                """.format(
                battle
            )
            R_BATTLE = requests.get(URL, params={"format": "json", "query": QUERY})
            try:
                battle_events.append(
                    R_BATTLE.json()["results"]["bindings"][0]["battle"]["value"].split(
                        "Q", 1
                    )[1]
                )
                print("Found wid for {}".format(battle))
            except IndexError:
                print("No wid for {}".format(battle))
        for treaty in row["peace treaties"].splitlines():
            if "(" in treaty:
                treaty_year = int(re.search(r"\((.+?)\)", treaty).group(1))
                treaty = treaty.split(" (")[0]
                URL = "https://query.wikidata.org/sparql"
                QUERY = """
                    SELECT DISTINCT ?treaty ?treatyLabel
                    WHERE
                    {{
                        ?treaty (wdt:P31/wdt:P279*) wd:Q131569.
                        ?treaty rdfs:label ?queryByTitle.
                        ?treaty wdt:P585 ?point_in_time.
                        FILTER(REGEX(?queryByTitle, "{}", "i"))
                        FILTER(YEAR(?point_in_time) = {})
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
                    }}
                    """.format(
                    treaty, treaty_year
                )
                R_TREATY = requests.get(URL, params={"format": "json", "query": QUERY})
                try:
                    treaty_events.append(
                        R_TREATY.json()["results"]["bindings"][0]["treaty"][
                            "value"
                        ].split("Q", 1)[1]
                    )
                    print("Found wid for {}".format(treaty))
                except IndexError:
                    print("No wid for {}".format(treaty))
            else:
                URL = "https://query.wikidata.org/sparql"
                QUERY = """
                    SELECT DISTINCT ?treaty ?treatyLabel
                    WHERE
                    {{
                        ?treaty (wdt:P31/wdt:P279*) wd:Q131569.
                        ?treaty rdfs:label ?queryByTitle.
                        FILTER(REGEX(?queryByTitle, "{}", "i"))
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
                    }}
                    """.format(
                    treaty
                )
                R_TREATY = requests.get(URL, params={"format": "json", "query": QUERY})
                try:
                    treaty_events.append(
                        R_TREATY.json()["results"]["bindings"][0]["treaty"][
                            "value"
                        ].split("Q", 1)[1]
                    )
                    print("Found wid for {}".format(treaty))
                except IndexError:
                    print("No wid for {}".format(treaty))

        narration_data = {
            "title": row["title"],
            "description": row["description"],
            "date_label": row["year"],
            "map_datetime": first_year_dt,
            "narrative": NARRATIVE_ID,
            "settings": ms_id,
            "img": row["pics"].splitlines()[0] if row["pics"] else "",
        }
        get_cd_by_wid = lambda wid: requests.get(
            os.getenv("API_ROOT", "http://localhost/api/")
            + "/cached-data?wikidata_id="
            + wid
        ).json()
        narration_data["attached_events_ids"] = list(
            filter(
                (None).__ne__,
                map(
                    lambda wid: int(get_cd_by_wid(wid)[0]["id"])
                    if get_cd_by_wid(wid)
                    else populate_cd(wid, wid in battle_events),
                    battle_events + treaty_events,
                ),
            )
        )

        r_narration = requests.post(
            os.getenv("API_ROOT", "http://localhost/api/") + "/narrations/",
            narration_data,
            params={"format": "json"},
        )
        print(
            "Narration '{}'// {}: {}".format(
                row["title"], str(r_narration.status_code), r_narration.reason
            )
        )
