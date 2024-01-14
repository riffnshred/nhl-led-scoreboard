import importlib.resources
import json

from typing import List, Optional

class Standings:
    def __init__(self, http_client):
        self.client = http_client

    def get_standings(self, date: Optional[str] = None, season: Optional[str] = None, cache = True) -> dict:
        if season:
            if cache:
                data_resource = importlib.resources.files("nhlpy") / "data"
                seasons = json.loads((data_resource / "seasonal_information_manifest.json").read_text())["seasons"]

            else:
                seasons = self.season_standing_manifest()

            season_data = next((s for s in seasons if s["id"] == int(season)), None)
            if not season_data:
                raise ValueError(f"Invalid Season Id {season}")

            date = season_data["standingsEnd"]

        res = date if date else "now"

        return self.client.get(resource=f"standings/{res}").json()

    def season_standing_manifest(self) -> List[dict]:
        return self.client.get(resource="standings-season").json()["seasons"]

    def get_score_details_by_date(self, date: str = None) -> dict:
        start_date = "2023-09-23"
        end_date = date
        cont = True
        games = {}

        while cont:
            week_data = self.client.get(resource=f"schedule/{start_date}").json()
            start_date = week_data["nextStartDate"]
            index = 0
            for day in week_data["gameWeek"]:
                for game in day["games"]:
                    if game["gameState"] == "FINAL" or game["gameState"] == "OFF":
                        game_id = game["id"]
                        home_id = game["homeTeam"]["abbrev"]
                        away_id = game["awayTeam"]["abbrev"]
                        home_score = game["homeTeam"]["score"]
                        away_score = game["awayTeam"]["score"]

                        games[index] = {"game_id" : game_id, "home_id" : home_id, "home_score" : home_score, "away_id" : away_id, "away_score": away_score}
                        index+=1
                    else:
                        cont = False
            
        return games
