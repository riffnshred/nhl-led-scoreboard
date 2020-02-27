"""
A Board is simply a display object with specific parameters made to be shown on screen.
    TODO: Make the board system customizable so that all the user needs to do is paste a board file and modify the
        config file to add the custom board.
"""
import debug
from boards.scoreticker import Scoreticker
from boards.standings import Standings
from boards.team_summary import TeamSummary
from boards.clock import Clock
from time import sleep


class Boards:
    def __init__(self):
        # self.standings_board = Standings(config, matrix)
        pass

    # Board handler for PushButton
    def _pb_board(self, data, matrix):
        #bord_index = 0
        #while True:
        board = getattr(self, data.config.pushbutton_state_triggered1)
        board(data, matrix)

        #    if bord_index >= (len(data.config.boards_off_day) - 1):
        #        return
        #    else:
        #        bord_index += 1

    # Board handler for Off day state
    def _off_day(self, data, matrix):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_off_day[bord_index])
            board(data, matrix)

            if bord_index >= (len(data.config.boards_off_day) - 1):
                return
            else:
                bord_index += 1

    def _scheduled(self, data, matrix):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_scheduled[bord_index])
            board(data, matrix)

            if bord_index >= (len(data.config.boards_scheduled) - 1):
                return
            else:
                bord_index += 1

    def _intermission(self, data, matrix):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_intermission[bord_index])
            board(data, matrix)

            if bord_index >= (len(data.config.boards_intermission) - 1):
                return
            else:
                bord_index += 1

    def _post_game(self, data, matrix):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_post_game[bord_index])
            board(data, matrix)

            if bord_index >= (len(data.config.boards_post_game) - 1):
                return
            else:
                bord_index += 1

    def fallback(self, data, matrix):
        Clock(data, matrix)

    def scoreticker(self, data, matrix):
        Scoreticker(data, matrix).render()

    def standings(self, data, matrix):
        Standings(data, matrix).render()

    def team_summary(self, data, matrix):
        TeamSummary(data, matrix).render()

        
