from nhlpy.http_client import HttpClient

class GameCenter:
    def __init__(self, http_client: HttpClient):
        self.client = http_client
        
    def boxscore(self, game_id: str) -> dict:
        return self.client.get(resource=f"gamecenter/{game_id}/boxscore").json()

    def play_by_play(self,game_id: str) -> dict:
        return self.client.get(resource=f"gamecenter/{game_id}/play-by-play").json()

    def landing(self,game_id: str) -> dict:
        return self.client.get(resource=f"gamecenter/{game_id}/landing").json()

    def score_now(self) -> dict:
        return self.client.get(resource="score/now").json()
