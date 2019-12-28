from datetime import datetime
from nhl_api import game_status_info, current_season_info

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

    def is_irregular(self, status):
        return status in self.Irregular

    def is_offseason(self, now=False):
        if not now:
            now = datetime.today().date()
        else:
            now = datetime.strptime(now, "%Y-%m-%d").date()

        regular_season_startdate = datetime.strptime(self.season_info['regularSeasonStartDate'], "%Y-%m-%d").date()
        end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()

        return now < regular_season_startdate or now > end_of_season

    def is_playoff(self, now=False):
        if not now:
            now = datetime.today().date()
        else:
            now = datetime.strptime(now, "%Y-%m-%d").date()
        print(now)
        regular_season_enddate = datetime.strptime(self.season_info['regularSeasonEndDate'], "%Y-%m-%d").date()
        end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()
        print(regular_season_enddate)
        return regular_season_enddate < now <= end_of_season