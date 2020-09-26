"""
    TODO: How this whole system works is getting complex for nothing and I need to recode this by sorting into seperate classes instead of having everything into a
        single one.
"""


from datetime import datetime, timedelta
from time import sleep
import debug
import nhl_api
from api.covid19.data import Data as covid19_data
from data.status import Status
from utils import get_lat_lng

NETWORK_RETRY_SLEEP_TIME = 0.5




def filter_list_of_games(games, teams):
    """
    Filter the list 'games' and keep only the games which the teams in the list 'teams' are part of.
    """
    return list(game for game in set(games) if {game.away_team_id, game.home_team_id}.intersection(set(teams)))

def filter_list_of_series(series, teams):
    """
    Filter the list 'single_series' and keep only the ones which the teams in the list 'teams' are part of.

        TODO: make a filter_list function that works for both list of games and list of series. need to add lost of attribute to look for and compare (intersection)
    """

    return list(single_series for single_series in set(series) if {single_series.matchupTeams[0].team.id, single_series.matchupTeams[1].team.id}.intersection(set(teams)))


def prioritize_pref_games(games, teams):
    """
    This one is a doozy. If you find a cleaner or more efficient way, please let me know.

    Ordered list of preferred games to match the order of their corresponding team and clean the 'None' element
    produced by the'map' function.

    return the cleaned game list. lemony fresh!!!
    """

    ordered_game_list = map(lambda team: next(
        (game for game in games if game.away_team_id == team or game.home_team_id == team), None),
                            teams)
    cleaned_game_list = list(filter(None, list(dict.fromkeys(ordered_game_list))))
    return cleaned_game_list

def prioritize_pref_series(series, teams):
    """
        Ordered list of preferred series to match the order of their corresponding team and clean the 'None' element
        produced by the'map' function.
    """
    ordered_series_list = map(lambda team: next(
        (single_series for single_series in series if single_series.matchupTeams[0].team.id == team or single_series.matchupTeams[1].team.id == team), None),
                            teams)
    cleaned_series_list = list(filter(None, list(dict.fromkeys(ordered_series_list))))
    return cleaned_series_list

class Data:
    def __init__(self, config):
        """
            TODO:
                - Rearrange the Teams info. (make one function instead of two)
                - Add Delay option to match the TV broadcast
                - Add Playoff data info.
                - Add Powerplay info
                - Make a Shootout layout with check boxes for each attempt
        :param config:
        """

        # Get lat/long for dimmer and weather
        self.latlng = get_lat_lng(config.location)
        # Test for alerts
        #self.latlng = [32.653,-83.7596]

        # Flag for if pushbutton has triggered
        self.pb_trigger = False

        # For pb state,  reboot or poweroff
        self.pb_state = None

        # Currently displayed board
        self.curr_board = None
        self.prev_board = None


        # Environment Canada manager (to share between the forecast, alerts and current obs)
        self.ecData = None
        # Weather Board Info
        self.wx_updated = False
        self.wx_units = []
        self.wx_current = []
        self.wx_curr_wind = []
        self.wx_curr_precip = []
        # Weather Alert Info
        self.wx_alerts = []
        self.wx_alert_interrupt = False

        #Weather Forecast Info
        self.forecast_updated = False
        self.wx_forecast = []

        # For update checker, True means new update available from github
        self.newUpdate = False
        self.UpdateRepo = "riffnshred/nhl-led-scoreboard"

        #For screensaver
        self.screensaver = False
        self.screensaver_displayed = False
        self.screensaver_livegame = False

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag for network issues
        self.network_issues = False

        # Get the teams info
        self.teams = self.get_teams()

        # Save the parsed config
        self.config = config

        # Initialize the time stamp. The time stamp is found only in the live feed endpoint of a game in the API
        # It shows the last time (UTC) the data was updated. EX 20200114_041103
        self.time_stamp = "00000000_000000"

        # Flag for when the data live feed of a game has updated
        self.new_data = True

        # Get each team's data from the teams info
        self.get_teams_info()

        # Get favorite team's id
        self.pref_teams = self.get_pref_teams_id()

        # Parse today's date and see if we should use today or yesterday
        self.refresh_current_date()

        # Set the pointer to the first game in the list of Pref Games
        self.current_game_index = 0

        # Fetch the games for today
        self.refresh_games()

        # Flag to indicate if all preferred games are Final
        self.all_pref_games_final = False

        # Today's date
        self.today = self.date()

        # Get the status from the API
        self.get_status()

        # Get refresh standings
        self.refresh_standings()

        # Fetch the playoff data
        self.refresh_playoff()

        self.isPlayoff = False

        # Stanley cup round flag
        self.stanleycup_round = False

        # Get Covid 19 Data
        self.covid19 = covid19_data()

    #
    # Date

    def __parse_today(self):
        today = datetime.today()
        noon = datetime.strptime("12:00", "%H:%M").replace(year=today.year, month=today.month,
                                                        day=today.day)
        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month,
                                                                                day=today.day)
        if noon < end_of_day < datetime.now() and datetime.now() > noon:
            today += timedelta(days=1)
        elif end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day

    def date(self):
        return datetime(self.year, self.month, self.day).date()

    def refresh_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    def _is_new_day(self):
        debug.info('Checking for new day')
        self.refresh_current_date()
        if self.today != self.date():
            debug.info('It is a new day, refreshing Data')

            # Set the pointer to the first game in the list of Pref Games
            self.current_game_index = 0

            # Today's date
            self.today = self.date()

            # Get the status info from the API
            self.get_status()

            # Get the teams info
            self.teams = self.get_teams()

            # Get favorite team's id
            self.pref_teams = self.get_pref_teams_id()

            # Reset flag
            self.all_pref_games_final = False

            # Reset and refresh Data
            self.refresh_data()
            return True
        else:
            debug.info("It is not a new day")
            return False

    #
    # Daily NHL Data

    def get_teams(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                teams = nhl_api.teams()
                self.network_issues = False
                return teams

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to Get the list of Teams. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def refresh_games(self):
        """
            Refresh the current list of games of the day.

            self.games : List of all the games happening today
            self.pref_games : List of games which the preferred teams are ordered by priority.

            If the user want's to rotate only his preferred games between the periods and during the day, save those
            only. Lastly, If if not an Off day for the pref teams, reorder the list in order of preferred teams and load
            the first game as the main event.
        """
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.games = nhl_api.day(self.year, self.month, self.day)
                self.pref_games = filter_list_of_games(self.games, self.pref_teams)
                if self.config.preferred_teams_only and self.pref_teams:
                    self.games = self.pref_games

                if not self.is_pref_team_offday():
                    self.pref_games = prioritize_pref_games(self.pref_games, self.pref_teams)
                    self.check_all_pref_games_final()

                    self.current_game_id = self.pref_games[self.current_game_index].game_id


                    # Remove the current game id (Main event) form the list of games.
                    if self.config.live_mode:
                        game_list = []
                        for game in self.games:
                            if game.game_id != self.current_game_id:
                                game_list.append(game)
                        self.games = game_list

                self.network_issues = False
                break

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the list of games. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

            except IndexError as error_message:
                debug.error(error_message)
                debug.info("All preferred games are Final, showing the top preferred game")
                self.current_game_index = 0
                self.all_pref_games_final = True
                self.refresh_games()

    def check_all_pref_games_final(self):
        for game in self.pref_games:
            if game.status != "Final":
                return

        self.all_pref_games_final = True


    # This is the function that will determine the state of the board (Offday, Gameday, Live etc...).
    def get_status(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.status = Status()
                break

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the Status data. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                self.status = []
                sleep(NETWORK_RETRY_SLEEP_TIME)


    #
    # Main game event data

    def refresh_overview(self):
        """
            Get a all the data of the main event.
        :return:
        """
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.overview = nhl_api.overview(self.current_game_id)
                if self.time_stamp != self.overview.time_stamp:
                    self.time_stamp = self.overview.time_stamp
                    self.new_data = True
                self.needs_refresh = False
                self.network_issues = False
                break
            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the Overview. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def _next_game(self):
        """
        function to show the next game of in the "pref_games" list.

        Check the status of the current preferred game and if it's Final or between periods rotate to the next game on
        the game list.

        :return:
        """
        if self.all_pref_games_final:
            return False

        self.current_game_index += 1
        self.refresh_games()
        return True

    #
    # Standings

    def refresh_standings(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.standings = nhl_api.standings()
                break

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the Standings. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    #
    # Teams

    def get_teams_info(self):
        try:
            info_by_id = {}
            for team in self.teams:
                info_by_id[team.team_id] = team

            self.teams_info = info_by_id
        except TypeError:
            self.teams_info = []

    def get_pref_teams_id(self):
        """
            Finds the preferred teams ID. The type of Team information variate throughout the API except for the team's id.
            Working with that will be much easier.

        :return: list of the preferred team's ID in order
        """
        try:
            allteams = self.teams
            pref_teams = self.config.preferred_teams
            allteams_id = {}
            pref_teams_id = []
            # Put all the team's in a dict with there name as KEY and ID as value.
            for team in allteams:
                allteams_id[team.team_name] = team.team_id

            # Go through the list of preferred teams name. If the team's name exist, put the ID in a new list.
            if pref_teams:
                for team in pref_teams:
                    if team in allteams_id:
                        pref_teams_id.append(allteams_id[team])
                    else:
                        debug.warning(team + " is not a team of the NHL. Make sure you typed team's name properly")

                return pref_teams_id
            else:
                return False
        except TypeError:
            return []

    #
    # Playoffs
    def refresh_playoff(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                # Get the plaoffs data from the nhl api
                self.playoffs = nhl_api.playoff(self.status.season_id)
                # Check if there is any rounds avaialable and grab the most recent one available.
                if self.playoffs.rounds:
                    self.current_round = self.playoffs.rounds[str(self.playoffs.default_round)]
                    self.current_round_name = self.current_round.names.name
                    if self.current_round_name == "Stanley Cup Qualifier":
                        self.current_round_name = "Qualifier"
                    if self.playoffs.default_round == 4:
                        self.stanleycup_round = True

                    debug.info("defaultround number is : {}".format(self.playoffs.default_round))
                    
                    try:
                        # Grab the series of the current round of playoff.
                        self.series = self.current_round.series

                        # Check if prefered team are part of the current round of playoff
                        self.pref_series = prioritize_pref_series(filter_list_of_series(self.series, self.pref_teams), self.pref_teams)

                        # If the user as set to show his favorite teams in the seriesticker
                        if self.config.seriesticker_preferred_teams_only and self.pref_series:
                            self.series = self.pref_series
                    except AttributeError:
                        debug.error("The {} Season playoff has to started yet or unavailable".format(self.playoffs.season))
                        self.isPlayoff = False
                        break

                    self.isPlayoff = True
                break

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the list of Series. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def series_by_conference():
        """
            TODO:reorganize the list of series by conference and return the list
        """
        pass

    #
    # Offdays

    def is_pref_team_offday(self):
        try:
            return not len(self.pref_games)
        except:
            return True

    def is_nhl_offday(self):
        try:
            return not len(self.games) and not len(self.pref_games)
        except:
            return True

    def refresh_data(self):
        """
            This method is used when the software move to the next day or . It reset all the main variables
            and re-initialize the overall data.
        :return:
        """
        debug.log("refresing data")
        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag for network issues
        self.network_issues = False

        # Parse today's date and see if we should use today or yesterday
        self.refresh_current_date()

        # Update team's data
        self.get_teams_info()

        # Update games for today
        self.refresh_games()

        # Update standings
        self.refresh_standings()

        # Update Playoff data
        self.refresh_playoff()

