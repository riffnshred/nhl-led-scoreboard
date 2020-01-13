from time import sleep
from datetime import datetime
import debug
from renderer.Scoreboard import Scoreboard
from renderer.Scoreticker import Scoreticker

class MainRenderer:
    def __init__(self, data):
        self.data = data
        self.status = self.data.status
        self.dummy_data = 'Papoute'

    def render(self):
        while True:
            debug.info('Rendering...')
            if self.status.is_offseason(self.data.date()):
                # Offseason (Show offseason related stuff)
                debug.info("It's offseason")
                self.__render_offday()
            else:
                # Season.
                if self.data.is_pref_team_offday():
                    debug.info("Your preferred teams are Off today")
                    self.__render_offday()
                elif self.data.is_nhl_offday():
                    debug.info("There is no game in the NHL today")
                    self.__render_offday()
                else:
                    debug.info("Game Day Wooooo")
                    self.__render_game_day()

    def __render_offday(self):
        while True:
            if self.data._is_new_day():
                debug.info('This is a new day')
                return
            print("Showing Offday")
            Scoreticker(self.data)

            sleep(5)

    def __render_game_day(self):
        debug.info("Showing Game")
        while True:
            if self.data._is_new_day():
                print('This is a new day')
                return

            if self.data.needs_refresh:
                self.data.refresh_current_date()
                self.data.refresh_overview()

            if self.status.is_live(self.data.overview.status):
                """ Live Game state """
                debug.info("Game is Live")
                self.__render_Live(self.data.overview)

            elif self.status.is_Final(self.data.overview.status):
                """ Post Game state """
                debug.info("Game Over")

            elif self.status.is_scheduled(self.data.overview.status):
                """ Pre-game state """
                debug.info("Game is Scheduled")

            Scoreboard(self.dummy_data).render()
            sleep(10)

    def __render_pregame(self):
        sleep(5)
        return

    def __render_postgame(self):
        debug.info("Showing Post-Game")
        Scoreboard(self.dummy_data).render()
        return

    def __render_Live(self, overview):
        while True:
            if overview.linescore.intermissionInfo.inIntermission:
                # Show Boards for Intermission
                debug.info("Game is in Intermission")
                return
            else:
                debug.info("Showing game Live")
                Scoreboard(self.dummy_data).render()
            sleep(5)

    def chk_time(self):
        self.now = datetime.now()
        self.now = self.now.strftime("%H:%M:%S")