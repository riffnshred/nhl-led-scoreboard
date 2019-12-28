"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""
import datetime
from nhl_api.utils import convert_time
import nhl_api.data
import nhl_api.object
import json

def scoreboard(year, month, day):
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = nhl_api.data.get_schedule(year, month, day)
    parsed = data.json()
    if parsed["dates"]:
        games_data = parsed["dates"][0]["games"]
        games = {}
        for game in games_data:
            game_id = game['gamePk']
            season = game['season']
            game_type = game['gameType']
            game_date = game['gameDate']

            home_team_id = int(game['teams']['home']['team']['id'])
            home_team_name = game['teams']['home']['team']['name']
            away_team_id = int(game['teams']['away']['team']['id'])
            away_team_name = game['teams']['away']['team']['name']
            home_score = game['teams']['home']['score']
            away_score = game['teams']['away']['score']

            status = game['status']['detailedState']
            status_code = game['status']['statusCode']
            status_abstract_state = game['status']['abstractGameState']

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
                'status_code': status_code,
                'status_abstract_state': status_abstract_state
            }

            # put this dictionary into the larger dictionary
            games[game_id] = output
    return games


class GameScoreboard(object):

    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d %I:%M")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})').format(self)

def overview(game_id):

    output = {}
    data = nhl_api.data.get_overview(game_id)
    data_string = json.loads(data.text)
    print(data_string)
    return data_string



class Overview(nhl_api.object.Object):
    pass