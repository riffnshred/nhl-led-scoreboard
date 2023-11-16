"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from nhl_api.utils import convert_time
import nhl_api.data
import nhl_api.object

from nhl_api_client import Client
# from nhl_api_client.api.play_by_play import get_schedule_by_date
from nhl_api_client.api.game import get_game_play_by_play_by_id
from nhl_api_client.models import PlayByPlay
from nhl_api_client.types import Response

def scoreboard(year, month, day):
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = nhl_api.data.get_schedule(year, month, day)
    if not data:
        return data
    parsed = data.json()

    if parsed["games"]:
        games_data = parsed["games"]
        games = {}
        for game in games_data:
            game_id = game['id']
            season = game['season']
            game_type = game['gameType']
            game_date = game['gameDate']

            htd = game['homeTeam']
            home_team_id = int(htd['id'])
            home_team_name = htd['abbrev']
            away_team_id = int(game['awayTeam']['id'])
            away_team_name = game['awayTeam']['abbrev']
            home_score = htd['score'] if 'score' in htd else 0
            away_score = 0 # game['awayTeam']['score']

            status = game['gameState']
            # status_code = game['status']['statusCode']
            # status_abstract_state = game['status']['abstractGameState']
            # linescore = game['linescore']

            output = {
                'game_id': game_id,
                'season': season,
                'game_type': game_type,
                'game_date': game_date,
                'home_team_id': home_team_id,
                'home_team_name': home_team_name,
                'away_team_id': away_team_id,
                'away_team_name': away_team_name,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                # 'status_code': status_code,
                # 'status_abstract_state': status_abstract_state,
                # All the linescore information (goals, sog, periods etc...)
                # 'linescore': linescore,
            }

            # put this dictionary into the larger dictionary
            games[game_id] = output
        return games
    else:
        return []


class GameScoreboard(object):

    def __init__(self, data):
        # loop through data
        # for x in data:
        #     # set information as correct data type
        #     try:
        #         setattr(self, x, int(data[x]))
        #     except ValueError:
        #         try:
        #             setattr(self, x, float(data[x]))
        #         except ValueError:
        #             # string if not number
        #             setattr(self, x, str(data[x]))
        #     except TypeError:
        #         obj = nhl_api.object.Object(data[x])
        #         setattr(self, x, obj)

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})').format(self)

    def __repr__(self):
        return self.__str__()


def overview(game_id):
    client = Client(base_url="https://api-web.nhle.com")
    game_details = {}
    with client as client:
        game_details = get_game_play_by_play_by_id.sync(game_id, client=client)

    return game_details