"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from nhl_api.utils import convert_time
import nhl_api.object

from nhlpy import NHLClient
# from nhl_api_client.api.play_by_play import get_schedule_by_date
#from nhlpy.api.game_center import boxscore

class GameScoreboard(object):
    def __init__(self, data):
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
    
    client = NHLClient(verbose=False)
    game_details = {}
    #with client as client:
    game_details = client.game_center.play_by_play(game_id)

    return game_details
