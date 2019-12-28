
from time import sleep
from datetime import datetime
from renderer.scoreboard_renderer import Scoreboard

def chk_state():
    pass

class MainRenderer:
    def __init__(self, data):
        self.data = data
        self.state = self.data.current_state

        # TO DELETE, Generic string for testing
        self.dummy_data = "Papoute"

    def render(self):
        while True:

            print(self.state)
            # Offseason (Show offseason related stuff)
            if self.state == "offseason":
                print("It's off season")
                self.__render_offday()
            else:
                # Gameday
                if self.state == "Scheduled":
                    print("Game is about to begin")
                elif self.state == "pre-game":
                    print("Game is about to begin")
                    self.__render_game()
                elif self.state == "Live":
                    print("Game is Live")
                    self.__render_game()
                elif self.state == "post-game" or self.state == "Final":
                    print("Game Over")
                else:
                    print("There is no game today")
                    self.__render_offday()
            #sleep(5)
    def __render_offday(self):
        while True:
            print("Showing Offday")
            Scoreboard(self.dummy_data).render()
            sleep(5)
            return

    def __render_game(self):
        while True:
            print("Showing Game")
            Scoreboard(self.dummy_data).render()
            sleep(5)
            return

    def __render_pregame(self):
        sleep(5)
        return

    def __render_postgame(self):
        while True:
            print("Showing Post-Game")
            Scoreboard(self.dummy_data).render()
            sleep(5)
            return

    def chk_time(self):
        self.now = datetime.now()
        self.now = self.now.strftime("%H:%M:%S")