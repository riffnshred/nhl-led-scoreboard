from nhlpy.api import teams, standings, schedule, game_center
from nhlpy.http_client import HttpClient
from nhlpy.config import ClientConfig

class NHLClient:
    def __init__(self,verbose: bool = False) -> None:
        self._config = ClientConfig(verbose = verbose)
        self._http_client = HttpClient(self._config)

        self.teams = teams.Teams(http_client = self._http_client)
        self.standings = standings.Standings(http_client = self._http_client)
        self.schedule = schedule.Schedule(http_client = self._http_client)
        self.game_center = game_center.GameCenter(http_client = self._http_client)

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_value, traceback):
       return

