"""
    Shows list of games.
"""
from time import sleep
from utils import center_obj
from data.scoreboard import GameSummaryBoard
from renderer.scoreboard import ScoreboardRenderer
from renderer.matrix import MatrixPixels
import debug

class Scoreticker:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.rotation_rate = self.data.config.scoreticker_rotation_rate
        self.matrix = matrix
        self.spacing = 3 # Number of pixel between each dot + 1
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        self.layout = self.data.config.config.layout.get_board_layout('scoreticker')

    def render(self):
        self.index = 0
        self.games = self.data.other_games()
        self.num_games = len(self.games)
        try:
            while not self.sleepEvent.is_set():
                self.matrix.clear()
                if self.index >= (len(self.games)):
                    return

                ScoreboardRenderer(self.data, self.matrix, GameSummaryBoard(self.games[self.index], self.data)).render()
                self.show_indicator()
                self.matrix.render()

                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                #sleep(self.rotation_rate)
                self.sleepEvent.wait(self.rotation_rate)

                self.index += 1

        except IndexError:
            debug.info("no game to display, you set preferred teams only or NHL OFF DAY today")
            return

    def show_indicator(self):
        """
            TODO: This function need to be coded a better way. but it works :D

            Carousel indicator.
        """
        align = 0
        spacing = 3

        # if there is more then 11 games, reduce the spacing of each dots
        if self.num_games > 10:
            spacing = 2

            # Move back the indicator by 1 pixel if the number of games is even.
            if self.num_games % 2:
              align = -1

        # Measure the width of the indicator and then center it on the screen
        indicator_length = (self.num_games * spacing) - (spacing - 1)

        pixels = []

        # Render the indicator
        for i in range(self.num_games):
            dot_position = ((spacing * i) - 1) + 1

            color = (70, 70, 70)
            if i == self.index:
                color = (255, 50, 50)

            pixels.append(
              MatrixPixels(
                ((align + dot_position), 0), 
                color
              )
            )

        self.matrix.draw_pixels_layout(
            self.layout.indicator_dots,
            pixels,
            (pixels[-1].position[0] - pixels[0].position[0], 1)
        )