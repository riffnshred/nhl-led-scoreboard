from datetime import datetime, timedelta
import time

from data import nhl_api_parser as nhlparser

class Data:
    def __init__(self, config):
        '''
            TODO:
                - Make a function to get the daily schedule and store the time and the event
                - Make a function to get the fav teams by team name.
                - Make a Scoreboard class  like the MLB one
                - Add Delay option to match TV broadcast
        :param config:
        '''
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag to determine when it's a new day
        self.new_day = False

        ### TESTING RENDERING ROUTINE
        # get favorite team's id
        self.pref_team_id = self.__get_teams_id()

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.get_teams_info = nhlparser.get_teams()

        # Fetch the games for today
        #self.refresh_games = nhlparser.fetch_games()

        # Look if favorite team play today
        self.refresh_fav_team_status()

        # Find which state the scoreboard should be
        self.check_state()

    #
    # Date

    def __parse_today(self):
        today = datetime.today()
        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month,
                                                                                day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day

    def set_date(self):
        return datetime(self.year, self.month, self.day)

    def get_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    #
    # NHL API Data

    def refresh_schedule(self):
        self.schedule = nhlparser.fetch_games()

    def refresh_fav_team_status(self):
        self.fav_team_game_today = nhlparser.check_if_game(self.pref_team_id)

    # This is the function that will determine the state of the board (Offday, Gameday, Live etc...).
    def check_state(self):
        print("checking state")
        self.current_state = "pre-game"

    #
    # Games

    def refresh_overview(self):
        self.overview = nhlparser.fetch_overview(self.pref_team_id)
        self.needs_refresh = False

    #
    # Standings

    #
    # Teams

    def __get_teams_id(self):
        '''
            Finds the teams ID. The type of Team information variate throughout the API except for the team's id.

        :return:
        '''

        if self.config.rotate_preferred_teams_only:
            teams = self.config.preferred_teams
        else:
            teams = False

        allteams = nhlparser.get_teams()
        keyset = set()
        for k in allteams:
            keyset.update(allteams[k])
        if teams:
            for team_name in teams:
                print(allteams[team_name].setdefault("id", 0))
        else:
            print(allteams[k].setdefault("id", 0))