from datetime import datetime, timedelta
import time
import collections
import debug
import nhl_api
from data.status import Status

class Data:
    def __init__(self, config):
        """
            TODO:
                - Add Delay option to match the TV broadcast
                - Add a network issues handler. (Show Red bar at bottom of screen)
                - Add Playoff data info. (research required)
        :param config:
        """
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # get favorite team's id
        self.pref_teams = self.get_pref_teams_id()

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Set the pointer to the first game in the list
        self.current_game_index = 0

        # Fetch the games for today
        self.refresh_games()

        # Get the status from the API
        self.get_status()

        ## Test state TO DELETE
        self.current_state = 'Pre-Game'

        print(self.status.is_playoff('2019-04-05'))

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
    # Daily NHL Data

    def refresh_games(self):
        """
            Refresh the current list of games of the day.

            self.games : List of all the games happening today
            self.pref_games : List of games which the preferred teams are ordered by priority.

            If the user want's to rotate only his preferred games between the periods and during the day, save those
            only. Lastly, If if not an Off day for the pref teams, reorder the list in order of preferred teams and load
            the first game.
        """
        self.games = nhl_api.day(self.year, self.month, self.day)
        self.pref_games = self.__filter_list_of_games(self.games, self.pref_teams)
        if self.config.preferred_teams_only and self.pref_teams:
            self.games = self.pref_games

        if not self.is_pref_team_offday():
            self.pref_games = self.__prioritize_pref_games(self.pref_games, self.pref_teams)
            self.current_game_id = self.pref_games[self.current_game_index]

    # This is the function that will determine the state of the board (Offday, Gameday, Live etc...).
    def get_status(self):
        self.status = Status()



    def __filter_list_of_games(self, games, teams):
        """
        Filter the list 'games' and keep only the games which the teams in the list 'teams' are part of.
        """
        return list(game for game in set(games) if set([game.away_team_id, game.home_team_id]).intersection(set(teams)))

    def __prioritize_pref_games(self, games, teams):
        """
        This one is a doozy. If you find a cleaner or more efficient way, please let me know.

        Order list of preferred games to match the order of their corresponding team and clean the 'None' element
        produced by the'map' function.

        return the cleaned game list. lemony fresh!!!
        """

        ordered_game_list = map(lambda team: next(
            (game for game in games if game.away_team_id == team or game.home_team_id == team), None),
                                teams)
        cleaned_game_list = list(filter(None, list(dict.fromkeys(ordered_game_list))))
        return cleaned_game_list

    #
    # Games data

    def refresh_overview(self):
        self.overview = nhl_api.overview(self.current_game_id)
        self.needs_refresh = False

    def advance_to_next_game(self):
        """
        function to show the next game of in the "games" list.

        Check the status of the current preferred game and if it's Final or between periods rotate to the next game on
        the game list.

        :return:
        """
        pass

    def __next_game_index(self):
        counter = self.current_game_index + 1
        if counter >= len(self.games):
            counter = 0
        return counter
    #
    # Standings

    #
    # Teams

    def get_pref_teams_id(self):
        """
            Finds the preferred teams ID. The type of Team information variate throughout the API except for the team's id.
            Working with that will be much easier.

        :return: list of the preferred team's ID in order
        """

        allteams = nhl_api.teams()
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

    #
    # Offdays

    def is_pref_team_offday(self):
        return not len(self.pref_games)

    def is_offday(self):
        return not len(self.games)