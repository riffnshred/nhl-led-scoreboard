from typing import List

from nhlpy.http_client import HttpClient


class Teams:
    def __init__(self, http_client: HttpClient) -> None:
        self.client = http_client
        self.base_url = 'https://api.nhle.com'
        self.api_ver = "/stats/rest/"

    def team_stats_summary(self, lang="en") -> List[dict]:
        return self.client.get_by_url(full_resource=f"{self.base_url}{self.api_ver}{lang}/team/summary").json()

    def teams_info(self) -> dict:
        data_resource = importlib.resources.files("nhlpy") / "data"
        teams_info = json.loads((data_resource / "teams_20232024.json").read_text())["teams"]
        return teams_info

    def roster(self, team_abbr: str, season: str) -> dict:
        return self.client.get(resource=f"roster/{team_abbr}{season}").json()

