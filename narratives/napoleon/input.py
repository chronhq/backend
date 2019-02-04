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
    print(wid)
    URL = "https://query.wikidata.org/sparql"
    QUERY = """
    SELECT ?event ?date ?coors
    WHERE 
    {{
        BIND(wd:Q{} as ?event)
        ?event wdt:P585 ?date.
        ?event wdt:P276 ?location.
        ?location wdt:P625 ?coors
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    """.format(
        wid
    )
    event_info = requests.get(URL, params={"format": "json", "query": QUERY}).json()[
        "results"
    ]["bindings"][0]
    cd_data = {
        "event_type": 178_561 if is_battle else 131_569,
        "wikidata_id": wid,
        "location": event_info["coors"]["value"],
        "date": event_info["date"]["value"],
    }
    new_cd = requests.post(
        os.getenv("API_ROOT", "http://localhost/api/") + "/cached-data/",
        cd_data,
        params={"format": "json"},
    )
    return new_cd["id"]

narrative_data = {
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
}
r_narrative = requests.post(
    os.getenv("API_ROOT", "http://localhost/api/") + "/narratives/",
    narrative_data,
    params={"format": "json"},
)
narrative_id = r_narrative.json()["id"]
print(
    "Narrative #{}// {}: {}".format(
        narrative_id, str(r_narrative.status_code), r_narrative.reason
    )
)

with open("data.csv", mode="r") as narrative_file:
    narrative_reader = csv.DictReader(narrative_file)
    first = True
    for row in narrative_reader:
        if first == True:
            print(f'Column names are {", ".join(row)}')
            first = False
        else:
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
                "MapSettings #{}// {}: {}".format(
                    ms_id, str(r_ms.status_code), r_ms.reason
                )
            )

            first_year = (
                row["year"].split("-")[0] if "-" in row["year"] else row["year"]
            )
            first_year_dt = datetime.strptime(first_year, "%Y")
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
                        R_BATTLE.json()["results"]["bindings"][0]["battle"][
                            "value"
                        ].split("Q", 1)[1]
                    )
                    print("Found wid for {}".format(battle))
                except IndexError:
                    print("No wid for {}".format(battle))
            for treaty in row["peace treaties"].splitlines():
                if "(" in treaty:
                    treaty_year = int(re.search(r"\((.+?)\)", treaty).group(1))
                    treaty = treaty.split(" (")[0]
                    print(treaty)
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
                    R_TREATY = requests.get(
                        URL, params={"format": "json", "query": QUERY}
                    )
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
                    R_TREATY = requests.get(
                        URL, params={"format": "json", "query": QUERY}
                    )
                    try:
                        treaty_events.append(
                            R_TREATY.json()["results"]["bindings"][0]["treaty"][
                                "value"
                            ].split("Q", 1)[1]
                        )
                        print("Found wid for {}".format(treaty))
                    except IndexError:
                        print("No wid for {}".format(treaty))

            print(battle_events)
            print(treaty_events)
            print(battle_events + treaty_events)
            narration_data = {
                "title": row["title"],
                "description": row["description"],
                "date_label": row["year"],
                "map_datetime": first_year_dt,
                "narrative": narrative_id,
                "settings": ms_id,
            }
            get_cd_by_wid = lambda wid: requests.get(
                os.getenv("API_ROOT", "http://localhost/api/")
                + "/cached-data?wikidata_id="
                + wid
            ).json()
            narration_data["attached_events"] = (
                list(
                    map(
                        lambda wid: int(get_cd_by_wid(wid)[0]["id"])
                        if get_cd_by_wid(wid)
                        else populate_cd(wid, wid in battle_events),
                        battle_events + treaty_events,
                    )
                ),
            )

            print(narration_data["attached_events"])

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
            if r_narration.status_code == 400:
                print(r_narration.json())
