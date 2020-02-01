from datetime import datetime
from nhl_api import game_status_info, current_season_info
import debug

class Status:
    def __init__(self):
        game_status = game_status_info()
        self.season_info = current_season_info()['seasons'][0]
        self.Preview = []
        self.Live = []
        self.Final = []
        self.Irregular = []

        for status in game_status:
            if status['code'] == '8' or status['code'] == '9':
                self.Irregular.append(status['detailedState'])
            elif status['abstractGameState'] == "Preview":
                self.Preview.append(status['detailedState'])
            elif status['abstractGameState'] == 'Live':
                self.Live.append(status['detailedState'])
            elif status['abstractGameState'] == 'Final':
                self.Final.append(status['detailedState'])

    def is_scheduled(self, status):
        return status in self.Preview

    def is_live(self, status):
        return status in self.Live

    def is_final(self, status):
        return status in self.Final

    def is_irregular(self, status):
        return status in self.Irregular

    def is_offseason(self, date):
        try:
            regular_season_startdate = datetime.strptime(self.season_info['regularSeasonStartDate'], "%Y-%m-%d").date()
            end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()
            return date < regular_season_startdate or date > end_of_season
        except:
            debug.error('The Argument provided for status.is_offseason is missing or not right.')
            return False

    def is_playoff(self, date):
        try:
            regular_season_enddate = datetime.strptime(self.season_info['regularSeasonEndDate'], "%Y-%m-%d").date()
            end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()
            return regular_season_enddate < date <= end_of_season
        except TypeError:
            debug.error('The Argument provided for status.is_playoff is missing or not right.')
            return False