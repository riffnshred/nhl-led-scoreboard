from datetime import datetime, date
from nhl_api import game_status_info, current_season_info, next_season_info
import debug

class Status:
    def __init__(self):
        game_status = [] # game_status_info()
        # self.season_info = current_season_info()['seasons'][0]
        #self.next_season_info = next_season_info()['seasons'][0]
        self.season_id = 20232024 # self.season_info["seasonId"]
        self.Preview = []
        self.Live = []
        self.GameOver = []
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
                # since July 2020, status code 6 is no longer part of Game over but Final
                if status['code'] == '5':
                    self.GameOver.append(status['detailedState'])
                else:
                    self.Final.append(status['detailedState'])
        
        # # Make sure that the next_season_info is not an empty list, if it is, make next_season = to current season
        
        # if not self.next_season_info:
        #     debug.info("Next season info unavailable, defaulting to Oct 1 of current year as start of new season")
        #     self.next_season_info = self.season_info
        #     # Arbitrarily set the regularSeasonStartDate to Oct 1 of current year
        #     self.next_season_info['regularSeasonStartDate'] = "{0}-10-01".format(date.today().year)
        
        # self.refresh_next_season()
        

    def is_scheduled(self, status):
        return status == "FUT" or status == "PRE"

    def is_live(self, status):
        return status == "LIVE" or status == "CRIT"

    def is_game_over(self, status):
        return status == "OFF"

    def is_final(self, status):
        return status == "FINAL"

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

    def is_playoff(self, date, playoff_obj):
        try:
            # Get dates of the planned end of regular season and end of season
            regular_season_enddate = datetime.strptime(self.season_info['regularSeasonEndDate'], "%Y-%m-%d").date()
            end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()

            return regular_season_enddate < date <= end_of_season and playoff_obj.rounds
        except TypeError:
            debug.error('The Argument provided for status.is_playoff is missing or not right.')
            return False
     
    def refresh_next_season(self):
        debug.info("Updating next season info")
        self.season_info = current_season_info()['seasons'][0]
        self.next_season_info = next_season_info()['seasons'][0]
        # Make sure that the next_season_info is not an empty list, if it is, make next_season = to current season
        
        if not self.next_season_info:
            debug.info("Next season info unavailable, defaulting to Oct 1 of current year as start of new season")
            self.next_season_info = self.season_info
            # Arbitrarily set the regularSeasonStartDate to Oct 1 of current year
            self.next_season_info['regularSeasonStartDate'] = "{0}-10-01".format(date.today().year)
            
           
    def next_season_start(self):
        return self.next_season_info['regularSeasonStartDate']

    