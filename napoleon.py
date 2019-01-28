from datetime import datetime
import csv
import requests
import os

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

with open("nar1.csv", mode="r") as narrative_file:
    narrative_reader = csv.DictReader(narrative_file)
    line_count = 0
    for row in narrative_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
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
            events = []
            for battle in row["battles"].splitlines():
                URL = "https://query.wikidata.org/sparql"
                QUERY = """
                SELECT DISTINCT ?battle ?battleLabel WHERE {{
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    ?battle (wdt:P31/wdt:P279*) wd:Q178561.
                    ?battle rdfs:label ?queryByTitle.
                    FILTER(REGEX(?queryByTitle, "{}", "i"))
                }}
                """.format(
                    battle
                )
                R_BATTLE = requests.get(URL, params={"format": "json", "query": QUERY})
                try:
                    events.append(
                        int(
                            R_BATTLE.json()["results"]["bindings"][0]["battle"][
                                "value"
                            ].split("Q", 1)[1]
                        )
                    )
                    print("Found wid for {}".format(battle))
                except IndexError:
                    print("No wid for {}".format(battle))
            for treaty in row["peace treaties"].splitlines():
                if "(" in treaty:
                    pass  # TODO: implement year checking
                else:
                    URL = "https://query.wikidata.org/sparql"
                    QUERY = """
                    SELECT DISTINCT ?treaty ?treatyLabel
                    WHERE
                    {{
                        ?treaty wdt:P31 wd:Q625298.
                        ?treaty rdfs:label ?queryByTitle.
                        FILTER(REGEX(?queryByTitle, "{}", "i"))
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
                    }}
                    """.format(
                        treaty
                    )  # TODO: also check sieges, output list of failed battles at end
                    R_TREATY = requests.get(
                        URL, params={"format": "json", "query": QUERY}
                    )
                    try:
                        events.append(
                            int(
                                R_TREATY.json()["results"]["bindings"][0]["treaty"][
                                    "value"
                                ].split("Q", 1)[1]
                            )
                        )
                        print("Found wid for {}".format(treaty))
                    except IndexError:
                        print("No wid for {}".format(treaty))

            narration_data = {
                "title": row["title"],
                "description": row["description"],
                "date_label": row["year"],
                "map_datetime": first_year_dt,
                "narrative": narrative_id,
                "settings": ms_id,
                "attached_events": events,
            }
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
