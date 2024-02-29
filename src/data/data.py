"""
    TODO: How this whole system works is getting complex for nothing and I need to recode this by sorting into seperate classes instead of having everything into a
        single one.
"""

from datetime import datetime, date, timedelta
from time import sleep
import debug
import nhl_api
from data.playoffs import Series
from data.status import Status
from utils import get_lat_lng, convert_time
import json

NETWORK_RETRY_SLEEP_TIME = 0.5




def filter_list_of_games(games, teams):
    """
    Filter the list 'games' and keep only the games which the teams in the list 'teams' are part of.
    """
    # print(games)
    # print(game['awayTeam']['id'], game['homeTeam']['id'])
    pref_games = []
    index = []
    prev_index = 0
    for game in games:
        if game["homeTeam"]["id"] in teams:
            index.append(teams.index(game["homeTeam"]["id"]))
            pref_games.append(game)
        elif game["awayTeam"]["id"] in teams:
            pref_games.append(game)
            index.append(teams.index(game["awayTeam"]["id"]))
    pref_games = [x for _,x in sorted(zip(index,pref_games))]
    # return list(game for game in games if {game['awayTeam']['id'], game['homeTeam']['id']}.intersection(set(30)))
    return pref_games

    # return list(game for game in set(games) if {game.away_team_id, game.home_team_id}.intersection(set(teams)))

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

    TODO: For V2, this needs to be changed to return game list in different order, instead of a single way. Having that handled by different methods is the way.... this is the way !!!!
    """
    ordered_game_list = map(lambda team: next(
        (game for game in games if game.away_team.id == team or game.home_team.id == team), None),
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

def game_by_schedule(games):
    """
    By default, the api return the list of games ordered by start time, the first ones to finish will be put at the top. This function just fix make sure the list stay ordred by the start
    """

    return sorted(games, key=lambda x: g.game_date)


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

        # Get lat/long and message (for debug) for dimmer and weather
        self.latlng, self.latlng_msg = get_lat_lng(config.location)

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
        self.teams_info = self.get_teams()
        # So oddly enough, there are a handful of situations where the API does not include the team_id
        # it's happening often enough that it's worth keeping a second teams_info that is keyed off of the
        # abbreviation instead of the the id
        self.teams_info_by_abbrev = self.get_teams_by_code()

        # Save the parsed config
        self.config = config

        # Initialize the time stamp. The time stamp is found only in the live feed endpoint of a game in the API
        # It shows the last time (UTC) the data was updated. EX 20200114_041103
        self.time_stamp = "00000000_000000"

        # Flag for when the data live feed of a game has updated
        self.new_data = True

        # Get the status from the API
        self.get_status()

        # Get favorite team's id
        self.pref_teams = self.get_pref_teams_id()

        # Parse today's date and see if we should use today or yesterday
        self.refresh_current_date()

        # Set the pointer to the first game in the list of Pref Games
        #self.current_game_index = 0

        # Fetch the games for today
        self.refresh_games()

        # Flag to indicate if all preferred games are Final
        self.all_pref_games_final = False

        # Today's date
        self.today = self.date()

        # Get refresh standings
        self.refresh_standings()

        # Playoff Flag
        self.isPlayoff = False

        # Stanley cup round flag
        self.stanleycup_round = False

        # Fetch the playoff data
        # self.refresh_playoff()

        # Stanley cup champions
        # self.cup_winner_id = self.check_stanley_cup_champion()

    #
    # Date
    def __parse_today(self):
        today = datetime.today()
        noon = datetime.strptime("12:00", "%H:%M").replace(year=today.year, month=today.month,
                                                        day=today.day)
        #end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month,day=today.day)
        end_of_day = datetime.strptime("03:00", "%H:%M").replace(year=today.year, month=today.month,day=today.day)
        if noon < end_of_day < datetime.now() and datetime.now() > noon:
            today += timedelta(days=1)
        elif end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day
        #return 2021, 1, 26

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
            #self.current_game_index = 0

            # Today's date
            self.today = self.date()

            # Refresh general data.
            self.refresh_daily()

            # Reset flag
            self.all_pref_games_final = False
            
            #Don't think this is needed to be called a second time
           #self.refresh_daily()           
            #self.status.refresh_next_season()
           
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
                teams = nhl_api.info.team_info()
                self.network_issues = False
                return teams

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to Get the list of Teams. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def get_teams_by_code(self):
        teams_data = {}
        for team in self.teams_info.values():
            teams_data[team.details.abbrev] = team
        return teams_data

    def refresh_games(self):
        """
            Refresh the current list of games of the day.

            self.games : List of all the games happening today
            self.pref_games : List of games which the preferred teams are ordered by priority.

            If the user want's to rotate only his preferred games between the periods and during the day, save those
            only. Lastly, If if not an Off day for the pref teams, reorder the list in order of preferred teams and load
            the first game as the main event.

            TODO:
                Add the option to start the earliest game in the preferred game list but change to the top one as soon as it start.
        """

        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                data = nhl_api.data.get_score_details("{}-{}-{}".format(str(self.year), str(self.month).zfill(2), str(self.day).zfill(2)))
                if not data:
                    self.games = []
                    self.pref_games = []
                    return data

                self.games = data["games"]
                self.pref_games = filter_list_of_games(self.games, self.pref_teams)
                # Populate the TeamInfo classes used for the team_summary board
                for team_id in self.pref_teams:
                    # import pdb; pdb.set_trace()
                    team_info = self.teams_info[team_id].details
                    pg, ng = nhl_api.info.team_previous_game(team_info.abbrev, str(date.today()))
                    team_info.previous_game = pg
                    team_info.next_game = ng

                if self.config.preferred_teams_only and self.pref_teams:
                    self.games = self.pref_games

                if not self.is_pref_team_offday() and self.config.live_mode:
                    #self.pref_games = prioritize_pref_games(self.pref_games, self.pref_teams)
                    self.check_all_pref_games_final()
                    # TODO: This shouldn't be needed to get the fact that your preferred team has a game today
                    self.check_game_priority()

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
                #self.current_game_index = 0
                self.all_pref_games_final = True
                self.refresh_games()

    def check_game_priority(self):
        """
            Function that handle the live game.

            Show the earliest game until the most prefered game start. 
            
            Always show the top team when the other games are final.
            
            If a higher game in priority starts, move to that one. 

            6:00 Final
            [7:00, *3:00, 7:00, 8:00, 10:00]

            9:45 (first game finished)
            [7:00, 7:00, 8:00, 10:00]
        """

        if len(self.pref_games) == 0:
            return
        
        self.current_game_id = self.pref_games[0]["id"]
        earliest_start_time = datetime.strptime(self.pref_games[0]["startTimeUTC"], '%Y-%m-%dT%H:%M:%SZ')
        #for g in self.pref_games:
        #    if earliest_start_time > datetime.strptime(g["startTimeUTC"], '%Y-%m-%dT%H:%M:%SZ'):
        #        earliest_start_time = datetime.strptime(g["startTimeUTC"], '%Y-%m-%dT%H:%M:%SZ')
        debug.info('checking highest priority game')
        for g in self.pref_games:
            if not self.status.is_final(g["gameState"]) and not g["gameState"]=="OFF":
                # If the game started.
                if datetime.strptime(g["startTimeUTC"],'%Y-%m-%dT%H:%M:%SZ') <= datetime.utcnow():
                    debug.info('Showing highest priority live game. {} vs {}'.format(g["awayTeam"]["name"]["default"], g["homeTeam"]["name"]["default"]))
                    self.current_game_id = g["id"]
                    return
                # If the game has not started but is ealier then the previous set game
                if datetime.strptime(g["startTimeUTC"], "%Y-%m-%dT%H:%M:%SZ") < earliest_start_time:
                    earliest_start_time = datetime.strptime(g["startTimeUTC"], '%Y-%m-%dT%H:%M:%SZ')
                    self.current_game_id = g["id"]
                    debug.info('Showing earliest game. {} vs {}'.format(g["awayTeam"]["name"]["default"], g["homeTeam"]["name"]["default"]))

    def other_games(self):
        if not self.is_pref_team_offday() and self.config.live_mode:
            game_list = []
            for g in self.games:
                if g["id"] != self.current_game_id:
                    game_list.append(g)

            return game_list
        return self.games

    def check_all_pref_games_final(self):
        for game in self.pref_games:
            if game["gameState"] != "OFF" or game["gameState"] != "FINAL":
                return

        self.all_pref_games_final = True

    
    # This is the function that will determine the state of the board (Offday, Gameday, Live etc...).
    def get_status(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                debug.info("getting status")
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
            Get all the data of the main event.
        """
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.overview = nhl_api.overview(self.current_game_id)
                # TODO: Not sure what was going on here
                if self.time_stamp != self.overview["clock"]["timeRemaining"]:
                    self.time_stamp = self.overview["clock"]["timeRemaining"]
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



    # TODO: Should probably move this into it's own TestClass of sorts
    def test_goal(self, data, matrix, sleepEvent):
        from data.scoreboard import Scoreboard
        from renderer.goal import GoalRenderer
        # f = open('test_scenarios/goal.json')
        f = open('test_scenarios/goal_unassisted.json')
        parsed = json.load(f)
        overview = PlayByPlay.from_dict(parsed)
        scoreboard = Scoreboard(overview, data)
        GoalRenderer(data, matrix, sleepEvent, scoreboard.home_team).render()

    """
        TODO: TO DELETE if the new check_game_priority() function works withtout a fuzz
    """
    # def _next_game(self):
    #     """
    #     function to show the next game of in the "pref_games" list.

    #     Check the status of the current preferred game and if it's Final or between periods rotate to the next game on
    #     the game list.

    #     :return:
    #     """
    #     if self.all_pref_games_final:
    #         return False

    #     self.current_game_index += 1
    #     self.refresh_games()
    #     return True

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
    #
    # Teams

    def get_pref_teams_id(self):
        """
            Finds the preferred teams ID. The type of Team information variate throughout the API except for the team's id.
            Working with that will be much easier.

        :return: list of the preferred team's ID in order
        """
        pref_teams = self.config.preferred_teams
        allteams_id = {}
        pref_teams_id = []
        # Put all the team's in a dict with there name as KEY and ID as value.
        for team_id, team in self.teams_info.items():
            allteams_id[team.details.name] = team_id

        # Go through the list of preferred teams name. If the team's name exist, put the ID in a new list.
        if pref_teams:
            for team in pref_teams:
                #Search for the team in the key
                res = {key: val for key, val in allteams_id.items() if team in key}
                pref_teams_id.append(list(res.values())[0])

            return pref_teams_id
        else:
            return False

    #
    # Playoffs
    def refresh_playoff(self):
        """
            Currently the series ticker request all the games of a series everytime its asked to load on screen.
            This create a lot of delay between showing each series. 
            TODO:
                Add a refresh function to the Series object instead and trigger a refresh only at specific time in the renderer.(End of a game, new day)
        """
        self.current_round = None
        self.current_round_name = None
        self.stanleycup_round = None
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
                    8478996
                    try:
                        self.series = []

                        # Grab the series of the current round of playoff.
                        self.series_list = self.current_round.series

                        # Check if prefered team are part of the current round of playoff
                        self.pref_series = prioritize_pref_series(filter_list_of_series(self.series_list, self.pref_teams), self.pref_teams)

                        # If the user as set to show his favorite teams in the seriesticker
                        if self.config.seriesticker_preferred_teams_only and self.pref_series:
                            self.series_list = self.pref_series
                        
                        for s in self.series_list:
                            self.series.append(Series(s,self))
                        
                        self.isPlayoff = True
                    except AttributeError:
                        debug.error("The {} Season playoff has not started yet or is unavailable".format(self.playoffs.season))
                        
                        self.isPlayoff = False
                        break
                break

            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the list of Series. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def check_stanley_cup_champion(self):
        if self.isPlayoff and self.stanleycup_round:
            for x in range(len(self.current_round.series[0].matchupTeams)):
                if self.current_round.series[0].matchupTeams[x].seriesRecord.wins >= 4:
                    return self.current_round.series[0].matchupTeams[x].team.id
                return

    def series_by_conference():
        """
            TODO:reorganize the list of series by conference and return the list. this is to allow the option of showing the preferred conference series.
        """
        pass

    #
    # Offdays

    def is_pref_team_offday(self):
        return len(self.pref_games) == 0

    def is_nhl_offday(self):
        return len(self.games) == 0

    def refresh_data(self):

        debug.info("refreshing data")
        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag for network issues
        self.network_issues = False

        # Parse today's date and see if we should use today or yesterday
        self.refresh_current_date()

        # Update games for today
        self.refresh_games()

    def refresh_daily(self):
        debug.info('refreshing daily data')
        self.teams_info = self.get_teams()
        self.teams_info_by_abbrev = self.get_teams_by_code()
        
        # Update standings
        self.refresh_standings()

        # Fetch the playoff data
        self.refresh_playoff()
        
 
        
