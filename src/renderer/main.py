from PIL import Image
from time import sleep
from datetime import datetime
import debug
from boards.boards import Boards
from boards.clock import Clock
from boards.stanley_cup_champions import StanleyCupChampions
from boards.seriesticker import Seriesticker
from boards.team_summary import TeamSummary
from boards.standings import Standings
from data.scoreboard import Scoreboard
from renderer.scoreboard import ScoreboardRenderer
from renderer.goal import GoalRenderer
from renderer.penalty import PenaltyRenderer
from utils import get_file
import random
import glob



class MainRenderer:
    def __init__(self, matrix, data, sleepEvent):
        self.matrix = matrix
        self.data = data
        self.status = self.data.status
        self.refresh_rate = self.data.config.live_game_refresh_rate
        self.boards = Boards()
        self.sleepEvent = sleepEvent
        self.sog_display_frequency = data.config.sog_display_frequency
        self.alternate_data_counter = 1

    def render(self):

        if self.data.config.testing_mode:
            debug.info("Rendering in Testing Mode")
            while True:
                self.data.refresh_overview()
                self.scoreboard = Scoreboard(self.data.overview, self.data)
                # ScoreboardRenderer(self.data, self.matrix, Scoreboard(game, self.data)).render()
                #Standings(self.data, self.matrix, self.sleepEvent).render()
                # self.data.test_goal(self.data, self.matrix, self.sleepEvent)
                #self._draw_event_animation("goal", self.scoreboard.home_team.id, self.scoreboard.home_team.name)
                GoalRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.away_team).render()
                #TeamSummary(self.data, self.matrix, self.sleepEvent).render()
                sleep(1)
                debug.info("Testing Mode Refresh")

        if self.data.config.test_goal_animation:
            debug.info("Rendering in Testing Mode")
            while True:
                self._draw_event_animation("goal",id=9)

        while self.data.network_issues:
            Clock(self.data, self.matrix, self.sleepEvent, duration=60)
            self.data.refresh_data()

        
        while True:
            debug.info('Rendering...')
            #if self.status.is_offseason(self.data.date()):
                # Offseason (Show offseason related stuff)
                #debug.info("It's offseason")
                #self.__render_offday()
            if self.data.config.testScChampions:
                self.test_stanley_cup_champion(self.data.config.testScChampions)

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

            self.data.refresh_data()

    def __render_offday(self):
        i = 0
        while True:
            debug.info('PING !!! Render off day')
            if self.data._is_new_day():
                debug.info('This is a new day')
                return
            self.boards._off_day(self.data, self.matrix,self.sleepEvent)

            if i >= 1:
                debug.info("off day data refresh")
                self.data.refresh_data()
                i = 0
            else:
                i += 1
            

    def __render_game_day(self):
        debug.info("Showing Game")
        # Initialize the scoreboard. get the current status at startup
        self.data.refresh_overview()
        self.scoreboard = Scoreboard(self.data.overview, self.data)
        self.away_score = self.scoreboard.away_team.goals
        self.home_score = self.scoreboard.home_team.goals
        self.away_penalties = self.scoreboard.away_team.penalties
        self.home_penalties = self.scoreboard.home_team.penalties
        # Cache to save goals and penalties and allow all the details to be collected on the API.
        self.goal_team_cache = []
        self.penalties_team_cache = []
        self.sleepEvent.clear()

        while not self.sleepEvent.is_set():

            if self.data._is_new_day():
                debug.log('This is a new day')
                return

            # Display the pushbutton board
            if self.data.pb_trigger:
                debug.info('PushButton triggered in game day loop....will display ' + self.data.config.pushbutton_state_triggered1 + ' board')
                if not self.data.screensaver:
                    self.data.pb_trigger = False
                #Display the board from the config
                self.boards._pb_board(self.data, self.matrix, self.sleepEvent)

            # Display the Weather Alert board
            if self.data.wx_alert_interrupt:
                debug.info('Weather Alert triggered in game day loop....will display weather alert board')
                self.data.wx_alert_interrupt = False
                #Display the board from the config
                self.boards._wx_alert(self.data, self.matrix, self.sleepEvent)

            # Display the screensaver board
            if self.data.screensaver:
                if not self.data.pb_trigger:
                    debug.info('Screensaver triggered in game day loop....')
                    #self.data.wx_alert_interrupt = False
                    #Display the board from the config
                    self.boards._screensaver(self.data, self.matrix, self.sleepEvent)
                else:
                    self.data.pb_trigger = False

            if self.status.is_live(self.data.overview["gameState"]):
                """ Live Game state """
                #blocks the screensaver from running if game is live
                self.data.screensaver_livegame = True
                debug.info("Game is Live")
                sbrenderer = ScoreboardRenderer(self.data, self.matrix, self.scoreboard)

                self.check_new_penalty()
                self.check_new_goals()
                self.__render_live(sbrenderer)
                if self.scoreboard.intermission:
                    debug.info("Main event is in Intermission")
                    # Show Boards for Intermission
                    self.draw_end_period_indicator()
                    self.sleepEvent.wait(self.refresh_rate)

                    self.check_new_penalty()
                    self.check_new_goals()
                    self.boards._intermission(self.data, self.matrix,self.sleepEvent)
                else:
                    self.sleepEvent.wait(self.refresh_rate)

            elif self.status.is_game_over(self.data.overview["gameState"]):
                debug.info("Game Over")
                sbrenderer = ScoreboardRenderer(self.data, self.matrix, self.scoreboard)
                self.check_new_goals()
                if self.data.isPlayoff and self.data.stanleycup_round:
                    self.data.check_stanley_cup_champion()
                    if self.data.cup_winner_id:
                        StanleyCupChampions(self.data, self.matrix, self.sleepEvent).render()

                self.__render_postgame(sbrenderer)
                self.sleepEvent.wait(self.refresh_rate)
                if not self.goal_team_cache:
                    self.boards._post_game(self.data, self.matrix,self.sleepEvent)

            elif self.status.is_final(self.data.overview["gameState"]):
                """ Post Game state """
                debug.info("FINAL")
                sbrenderer = ScoreboardRenderer(self.data, self.matrix, self.scoreboard)
                self.check_new_goals()
                if self.data.isPlayoff and self.data.stanleycup_round:
                    self.data.check_stanley_cup_champion()
                    if self.data.cup_winner_id:
                        StanleyCupChampions(self.data, self.matrix, self.sleepEvent).render()
                self.__render_postgame(sbrenderer)

                self.sleepEvent.wait(self.refresh_rate)
                if not self.goal_team_cache:
                    self.boards._post_game(self.data, self.matrix,self.sleepEvent)

            elif self.status.is_scheduled(self.data.overview["gameState"]):
                """ Pre-game state """
                debug.info("Game is Scheduled")
                sbrenderer = ScoreboardRenderer(self.data, self.matrix, self.scoreboard)
                self.__render_pregame(sbrenderer)
                #sleep(self.refresh_rate)
                self.sleepEvent.wait(self.refresh_rate)
                self.boards._scheduled(self.data, self.matrix,self.sleepEvent)

            elif self.status.is_irregular(self.data.overview["gameState"]):
                """ Pre-game state """
                debug.info("Game is irregular")
                sbrenderer = ScoreboardRenderer(self.data, self.matrix, self.scoreboard)
                self.__render_irregular(sbrenderer)
                #sleep(self.refresh_rate)
                self.sleepEvent.wait(self.refresh_rate)
                self.boards._scheduled(self.data, self.matrix,self.sleepEvent)
            else:
                print("somethin' really goofy")
                self.sleepEvent.wait(self.refresh_rate)
            self.data.refresh_data()
            self.data.refresh_overview()
            self.scoreboard = Scoreboard(self.data.overview, self.data)
            if self.data.network_issues:
                self.matrix.network_issue_indicator()

            if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                self.matrix.update_indicator()


    def __render_pregame(self, sbrenderer):
        debug.info("Showing Pre-Game")
        self.matrix.clear()
        sbrenderer.render()


    def __render_postgame(self, sbrenderer):
        debug.info("Showing Post-Game")
        self.matrix.clear()
        sbrenderer.render()
        self.draw_end_of_game_indicator()


    def __render_live(self, sbrenderer):
        debug.info("Showing Main Event")
        self.matrix.clear()
        sbrenderer.show_SOG = False
        if self.alternate_data_counter % self.sog_display_frequency == 0:
            sbrenderer.show_SOG = True
        sbrenderer.render()
        self.alternate_data_counter += 1

    def __render_irregular(self, sbrenderer):
        debug.info("Showing Irregular")
        self.matrix.clear()
        sbrenderer.render()


    def check_new_goals(self):
        debug.log("Check new goal")
        pref_team_only = self.data.config.goal_anim_pref_team_only
        away_id = self.scoreboard.away_team.id
        away_name = self.scoreboard.away_team.name
        away_goals = self.scoreboard.away_team.goals
        away_score = self.away_score
        home_id = self.scoreboard.home_team.id
        home_name = self.scoreboard.home_team.name
        home_goals = self.scoreboard.home_team.goals
        home_score = self.home_score
        # Display goal details that are cached if there is any
        # GoalRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.away_team).render()
        if self.goal_team_cache:
            try:
                while self.goal_team_cache:
                    # create a goal object first to see if there are any missing data
                    if self.goal_team_cache[0] == "away":
                        GoalRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.away_team).render()
                    else:
                        GoalRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.home_team).render()
                    # Remove the first cached goal
                    self.goal_team_cache.pop(0)
            except IndexError:
                debug.error("The scoreboard object failed to get the goal details, trying on the next data refresh")
            except KeyError:
                debug.error("Last Goal is a No goal. Or the API is missing some information.")
                self.goal_team_cache.pop(0)

        if away_score < away_goals:
            self.away_score = away_goals
            self.goal_team_cache.append("away")
            if away_id not in self.data.pref_teams and pref_team_only:
                return
            # run the goal animation
            self._draw_event_animation("goal", away_id, away_name)


        if home_score < home_goals:
            self.home_score = home_goals
            self.goal_team_cache.append("home")
            if home_id not in self.data.pref_teams and pref_team_only:
                return
            # run the goal animation
            self._draw_event_animation("goal", home_id, home_name)

    def check_new_penalty(self):
        debug.log("Check new penalty")

        #pref_team_only = self.data.config.penalty_anim_pref_team_only
        away_id = self.scoreboard.away_team.id
        away_name = self.scoreboard.away_team.name
        away_data_penalties = self.scoreboard.away_team.penalties
        a_penalties = self.away_penalties
        home_id = self.scoreboard.home_team.id
        home_name = self.scoreboard.home_team.name
        home_data_penalties = self.scoreboard.home_team.penalties
        h_penalties = self.home_penalties
        # Display goal details that are cached if there is any
        if self.penalties_team_cache:
            try:
                while self.penalties_team_cache:
                    # create a goal object first to see if there are any missing data
                    if self.penalties_team_cache[0] == "away":
                        PenaltyRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.away_team).render()
                    else:
                        PenaltyRenderer(self.data, self.matrix, self.sleepEvent, self.scoreboard.home_team).render()
                    # Remove the first cached goal
                    self.penalties_team_cache.pop(0)
            except IndexError as error:
                debug.error("The Penalty object failed to get the Penalty details, trying on the next data refresh")
                print(error)
            except AttributeError as error:
                debug.error("The Penalty object failed to get the Penalty details, trying on the next data refresh")
                print(error)

        if len(a_penalties) < len(away_data_penalties):
            self.away_penalties = away_data_penalties
            self.penalties_team_cache.append("away")
            #if away_id not in self.data.pref_teams: and pref_team_only:
            #    return
            # run the penalty animation
            self._draw_event_animation("penalty", away_id, away_name)

        if len(h_penalties) < len(home_data_penalties):
            self.home_penalties = home_data_penalties
            self.penalties_team_cache.append("home")
            #if home_id not in self.data.pref_teams: #and pref_team_only:
            #    return
            # run the penalty animation
            self._draw_event_animation("penalty", home_id, home_name)

    def _draw_event_animation(self, event, id=14, name="test"):
        preferred_team_only = self.data.config.goal_anim_pref_team_only
        # Get the list of gif's under the preferred and opposing directory
        ANIMATIONS = "assets/animations/{}".format(event)
        general_gifs = glob.glob("{}/general/*.gif".format(ANIMATIONS))
        preferred_gifs = glob.glob("{}/preferred/*.gif".format(ANIMATIONS))
        opposing_gifs = glob.glob("{}/opposing/*.gif".format(ANIMATIONS))

        if event == "goal":
            filename = "{}/goal_light_animation.gif".format(ANIMATIONS)
        elif event == "penalty":
            filename = "{}/penalty_animation.gif".format(ANIMATIONS)

        # Use alternate animations if there is any in the respective folder
        if general_gifs:
            # Set opposing team goal animation here
            filename = random.choice(general_gifs)
            debug.info("General animation is: " + filename)

        if opposing_gifs and not preferred_team_only:
            # Set opposing team goal animation here
            filename = random.choice(opposing_gifs)
            debug.info("Opposing animation is: " + filename)

        if id in self.data.pref_teams and preferred_gifs:
            # Set your preferred team goal animation here
            filename = random.choice(preferred_gifs)
            debug.info("Preferred animation is: " + filename)

        self.play_gif(filename)

    def play_gif(self, file):
        im = Image.open(get_file(file))

        # Set the frame index to 0
        frame_nub = 0
        # Set number of loop to 1 (if you want to play you animation more then once, change this variable)
        numloop = 1
        self.matrix.clear()

        # Go through the frames
        x = 0
        while x is not numloop:
            try:
                im.seek(frame_nub)
            except EOFError:
                x += 1
                if x == numloop:
                    return
                frame_nub = 0
                im.seek(frame_nub)

            self.matrix.draw_image(("50%", 0), im, "center")
            self.matrix.render()

            frame_nub += 1
            self.sleepEvent.wait(0.1)


    def draw_end_period_indicator(self):
        """TODO: change the width depending how much time is left to the intermission"""
        color = 255 # self.matrix.graphics.Color(0, 255, 0)
        # self.matrix.graphics.DrawLine(self.matrix.matrix, (self.matrix.width * .5) - 8, self.matrix.height - 2, (self.matrix.width * .5) + 8, self.matrix.height - 2, color)
        self.matrix.draw.line(((self.matrix.width * .5) - 8, self.matrix.height - 2, (self.matrix.width * .5) + 8, self.matrix.height - 2), fill=color)
        # self.matrix.graphics.DrawLine(self.matrix.matrix, (self.matrix.width * .5) - 9, self.matrix.height - 1, (self.matrix.width * .5) + 9, self.matrix.height - 1, color)
        self.matrix.draw.line(((self.matrix.width * .5) - 9, self.matrix.height - 1, (self.matrix.width * .5) + 9, self.matrix.height - 1), fill=color)
        self.matrix.render()

    def draw_end_of_game_indicator(self):
        """TODO: change the width depending how much time is left to the intermission"""
        color = 255 # self.matrix.graphics.Color(255, 0, 0)
        # self.matrix.graphics.DrawLine(self.matrix.matrix, (self.matrix.width * .5) - 8, self.matrix.height - 2, (self.matrix.width * .5) + 8, self.matrix.height - 2, color)
        self.matrix.draw.line(((self.matrix.width * .5) - 8, self.matrix.height - 2, (self.matrix.width * .5) + 8, self.matrix.height - 2), fill=color)
        # self.matrix.graphics.DrawLine(self.matrix.matrix, (self.matrix.width * .5) - 9, self.matrix.height - 1, (self.matrix.width * .5) + 9, self.matrix.height - 1, color)
        self.matrix.draw.line(((self.matrix.width * .5) - 9, self.matrix.height - 1, (self.matrix.width * .5) + 9, self.matrix.height - 1), fill=color)
        self.matrix.render()

    def test_stanley_cup_champion(self, team_id):
        self.data.cup_winner_id = team_id
        StanleyCupChampions(self.data, self.matrix, self.sleepEvent).render()
