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
from boards.covid_19 import Covid_19
from boards.pbdisplay import pbDisplay
from time import sleep


class Boards:
    def __init__(self):
        # self.standings_board = Standings(config, matrix)
        pass

    # Board handler for PushButton
    def _pb_board(self, data, matrix,sleepEvent):
        
        board = getattr(self, data.config.pushbutton_state_triggered1)
        board(data, matrix,sleepEvent)

    # Board handler for Off day state
    def _off_day(self, data, matrix,sleepEvent):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_off_day[bord_index])
            data.curr_board = data.config.boards_scheduled[bord_index]

            if data.pb_trigger:
                debug.info('PushButton triggered....will display ' + data.config.pushbutton_state_triggered1 + ' board ' + "Overriding off_day -> " + data.config.boards_off_day[bord_index])
                data.pb_trigger = False
                board = getattr(self,data.config.pushbutton_state_triggered1)
                data.curr_board = data.config.pushbutton_state_triggered1
                bord_index -= 1
    
            board(data, matrix,sleepEvent)

            if bord_index >= (len(data.config.boards_off_day) - 1):
                return
            else:
                if not data.pb_trigger:
                   bord_index += 1

    def _scheduled(self, data, matrix,sleepEvent):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_scheduled[bord_index])
            data.curr_board = data.config.boards_scheduled[bord_index]
            if data.pb_trigger:
                debug.info('PushButton triggered....will display ' + data.config.pushbutton_state_triggered1 + ' board ' + "Overriding scheduled -> " + data.config.boards_scheduled[bord_index])
                data.pb_trigger = False
                board = getattr(self,data.config.pushbutton_state_triggered1)
                data.curr_board = data.config.pushbutton_state_triggered1
                bord_index -= 1

            board(data, matrix,sleepEvent)

            if bord_index >= (len(data.config.boards_scheduled) - 1):
                return
            else:
                if not data.pb_trigger:
                   bord_index += 1

    def _intermission(self, data, matrix,sleepEvent):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_intermission[bord_index])
            data.curr_board = data.config.boards_scheduled[bord_index]

            if data.pb_trigger:
                debug.info('PushButton triggered....will display ' + data.config.pushbutton_state_triggered1 + ' board ' + "Overriding intermission -> " + data.config.boards_intermission[bord_index])
                data.pb_trigger = False
                board = getattr(self,data.config.pushbutton_state_triggered1)
                data.curr_board = data.config.pushbutton_state_triggered1
                bord_index -= 1

            board(data, matrix,sleepEvent)

            if bord_index >= (len(data.config.boards_intermission) - 1):
                return
            else:
                if not data.pb_trigger:
                   bord_index += 1

    def _post_game(self, data, matrix,sleepEvent):
        bord_index = 0
        while True:
            board = getattr(self, data.config.boards_post_game[bord_index])
            data.curr_board = data.config.boards_post_game[bord_index]

            if data.pb_trigger:
                debug.info('PushButton triggered....will display ' + data.config.pushbutton_state_triggered1 + ' board ' + "Overriding post_game -> " + data.config.boards_post_game[bord_index])
                data.pb_trigger = False
                board = getattr(self,data.config.pushbutton_state_triggered1)
                data.curr_board = data.config.pushbutton_state_triggered1
                bord_index -= 1

            board(data, matrix,sleepEvent)

            if bord_index >= (len(data.config.boards_post_game) - 1):
                return
            else:
                if not data.pb_trigger:
                   bord_index += 1

    def fallback(self, data, matrix, sleepEvent):
        Clock(data, matrix, sleepEvent)

    def scoreticker(self, data, matrix,sleepEvent):
        Scoreticker(data, matrix, sleepEvent).render()

    def standings(self, data, matrix,sleepEvent):
        #Try making standings a thread
        Standings(data, matrix, sleepEvent).render()

    def team_summary(self, data, matrix,sleepEvent):
        TeamSummary(data, matrix, sleepEvent).render()

    def clock(self, data, matrix,sleepEvent):
        Clock(data, matrix, sleepEvent)  

    def pbdisplay(self, data, matrix,sleepEvent):
        pbDisplay(data, matrix, sleepEvent)   

    def covid_19(self, data, matrix,sleepEvent):
        Covid_19(data, matrix, sleepEvent)   
