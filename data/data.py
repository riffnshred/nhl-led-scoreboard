from datetime import datetime, timedelta
import data.nhl_api_parser as nhlparser
import debug
import time

class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.get_teams_info()

        # Fetch the games for today
        self.refresh_games()



    def __parse_today(self):
        if self.config.demo_date:
            today = datetime.strptime(self.config.demo_date, '%Y-%m-%d')
        else:
            today = datetime.today()

        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)
        return (today.year, today.month, today.day)

    def set_date(self):
        return datetime(self.year, self.month, self.day)

    def get_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    def get_teams_info(self):
        return nhlparser.get_teams()

    def refresh_games(self,start_date = None):
        return nhlparser.fetch_games(start_date)
