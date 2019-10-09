from datetime import datetime, timedelta
import nhl_api_parser as nhlparser
import debug
import time

class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # get favorite team's id
        self.fav_team_id = self.config.fav_team_id

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.get_teams_info = nhlparser.get_teams()

        # Look if favorite team play today
        self.fav_team_game_today = nhlparser.check_if_game(self.fav_team_id)

        # Fetch the games for today
        self.refresh_games = nhlparser.fetch_games()

    def __parse_today(self):
        if self.config.demo_date:
            today = datetime.strptime(self.config.demo_date, '%Y-%m-%d')
        else:
            today = datetime.today()

        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)
        return today.year, today.month, today.day

    def set_date(self):
        return datetime(self.year, self.month, self.day)

    def get_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    def refresh_overview(self):
        self.overview = nhlparser.fetch_overview(self.fav_team_id)
        self.needs_refresh = False
