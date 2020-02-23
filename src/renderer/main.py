from PIL import Image
from time import sleep
from datetime import datetime
import debug
from boards.boards import Boards
from data.scoreboard import Scoreboard
from renderer.scoreboard import ScoreboardRenderer
from utils import get_file


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.status = self.data.status
        self.refresh_rate = self.data.config.live_game_refresh_rate
        self.boards = Boards()

    def render(self):
        while self.data.network_issues:
            self.matrix.network_issue_indicator()
            self.data.refresh_data()

        while True:
            try:
                debug.info('Rendering...')
                if self.status.is_offseason(self.data.date()):
                    # Offseason (Show offseason related stuff)
                    debug.info("It's offseason")
                    self.__render_offday()
                else:
                    # Season.
                    if not self.data.config.live_mode:
                        debug.info("Live mode is off. Going through the boards")
                        self.__render_offday()
                    elif self.data.is_pref_team_offday():
                        debug.info("Your preferred teams are Off today")
                        self.__render_offday()
                    elif self.data.is_nhl_offday():
                        debug.info("There is no game in the NHL today")
                        self.__render_offday()
                    else:
                        debug.info("Game Day Wooooo")
                        self.__render_game_day()

            except AttributeError as e:
                print(e)
                self.data.refresh_data()
                self.status = self.data.status

    def __render_offday(self):
        while True:
            debug.log('PING !!! Render off day')
            if self.data._is_new_day():
                debug.info('This is a new day')
                return
            self.data.refresh_games()
            self.data.refresh_standings()
            self.boards._off_day(self.data, self.matrix)

    def __render_game_day(self):
        debug.info("Showing Game")
        # Initialize the scoreboard. get the current status at startup
        self.data.refresh_overview()
        self.scoreboard = Scoreboard(self.data.overview, self.data.teams_info)
        self.away_score = self.scoreboard.away_team.goals
        self.home_score = self.scoreboard.home_team.goals
        while True:
            if self.data._is_new_day():
                debug.log('This is a new day')
                return

            if self.data.needs_refresh:
                print("refreshing")
                self.data.refresh_current_date()
                self.data.refresh_overview()
                self.data.refresh_games()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()

            if self.status.is_live(self.data.overview.status):
                """ Live Game state """
                debug.info("Game is Live")
                self.scoreboard = Scoreboard(self.data.overview, self.data.teams_info)
                self.check_new_goals()
                self.__render_live(self.scoreboard)

            elif self.status.is_final(self.data.overview.status):
                """ Post Game state """
                debug.info("Game Over")
                self.scoreboard = Scoreboard(self.data.overview, self.data.teams_info)
                self.__render_postgame(self.scoreboard)


            elif self.status.is_scheduled(self.data.overview.status):
                """ Pre-game state """
                debug.info("Game is Scheduled")
                self.scoreboard = Scoreboard(self.data.overview, self.data.teams_info)
                self.__render_pregame(self.scoreboard)

    def __render_pregame(self, scoreboard):
        debug.info("Showing Main Event")
        self.matrix.clear()
        ScoreboardRenderer(self.data, self.matrix, scoreboard).render()
        sleep(self.refresh_rate)
        self.boards._scheduled(self.data, self.matrix)
        self.data.needs_refresh = True

    def __render_postgame(self, scoreboard):
        debug.info("Showing Post-Game")
        self.matrix.clear()
        ScoreboardRenderer(self.data, self.matrix, scoreboard).render()
        self.draw_end_period_indicator()
        sleep(self.refresh_rate)
        self.boards._post_game(self.data, self.matrix)
        self.data.needs_refresh = True

    def __render_live(self, scoreboard):
        debug.info("Showing Main Event")
        self.matrix.clear()
        ScoreboardRenderer(self.data, self.matrix, scoreboard).render()
        if scoreboard.intermission:
            # Show Boards for Intermission
            self.draw_end_period_indicator()
            debug.info("Main event is in Intermission")
            self.boards._intermission(self.data, self.matrix)
        self.data.needs_refresh = True
        sleep(self.refresh_rate)

    def check_new_goals(self):
        debug.log("Check new goal")
        if self.away_score < self.scoreboard.away_team.goals:
            self.away_score = self.scoreboard.away_team.goals
            self._draw_goal(self.scoreboard.away_team.id, self.scoreboard.away_team.name)
        if self.home_score < self.scoreboard.home_team.goals:
            self.home_score = self.scoreboard.home_team.goals
            self._draw_goal(self.scoreboard.home_team.id, self.scoreboard.home_team.name)

    def _draw_goal(self, id, name):
        debug.info('Score by team: ' + name)
        # Set opposing team goal animation here
        filename = "assets/animations/goal_light_animation.gif"
        if id in self.data.pref_teams:
            # Set your preferred team goal animation here
            filename = "assets/animations/goal_light_animation.gif"

        im = Image.open(get_file(filename))

        # Set the frame index to 0
        frame_nub = 0

        self.matrix.clear()

        # Go through the frames
        x = 0
        while x is not 5:
            try:
                im.seek(frame_nub)
            except EOFError:
                x += 1
                frame_nub = 0
                im.seek(frame_nub)

            self.matrix.draw_image((0, 0), im)
            self.matrix.render()

            frame_nub += 1
            sleep(0.1)

    def draw_end_period_indicator(self):
        """TODO: change the width depending how much time is left to the intermission"""
        color = self.matrix.graphics.Color(0, 255, 0)
        self.matrix.graphics.DrawLine(self.matrix.matrix, 23, self.matrix.height - 2, 39, self.matrix.height - 2, color)
        self.matrix.graphics.DrawLine(self.matrix.matrix, 22, self.matrix.height - 1, 40, self.matrix.height - 1,
                                      color)
