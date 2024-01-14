from typing import Optional, List
from nhlpy.http_client import HttpClient
import datetime

class Schedule:
    def __init__(self, http_client: HttpClient) -> None:
        self.client = http_client

    def get_scheule(self,date: Optional[str] = None) -> dict:
        res = date if date else "now"
        return self.client.get(resource=f"schedule/{res}").json()

    def get_schedule_by_team_by_month(self,teamm_abbr: str, month: Optional[str] = None) -> List[dict]:
        resource = f"club-schedule/{team_abbr}/month/{month if month else 'now'}"
        return self.client.get(resource=resource).json()["games"]

    def get_schedule_by_team_by_week(self,team_abbr: str, date: Optional[str] = None) -> List[dict]:
        if date is None:
            date = datetime.date.today()
        resource = f"club-schedule/{team_abbr}/week/{date}"
        return self.client.get(resource=resource).json()

    def get_season_schedule(self, team_abbr: str, season: str) -> dict:
        return self.client.get(resource=f"club-schedule-season/{team_abbr}/{season}").json()

    def schedule_calendar(self, date: str) -> dict:
        return self.client.get(resource=f"schedule-calendar/{date}").json()

