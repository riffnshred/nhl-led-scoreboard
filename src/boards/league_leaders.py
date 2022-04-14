from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
import re
import debug
from time import sleep
from utils import center_text


class Leaders:
    def __init__(self, data, matrix, sleepEvent):

        self.data = data
        
        self.matrix = matrix
        self.layout = self.data.config.config.layout.get_board_layout('league_leaders')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.draw_leaders()

    def draw_leaders(self):
        self.matrix.clear()
        # draw a row of pixels from 7, 0 to 7, 32


        if self.data.config.point_leaders:
            self.matrix.clear()

            self.matrix.draw_text_layout(
                self.layout.name,
                "point leaders",
                backgroundColor=(255,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.point_leaders.get('data')[0].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.point_leaders.get('data')[1].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.point_leaders.get('data')[2].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.point_leaders.get('data')[3].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.point_leaders.get('data')[0].get('points')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.point_leaders.get('data')[1].get('points')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.point_leaders.get('data')[2].get('points')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.point_leaders.get('data')[3].get('points')}"
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.goal_leaders:
            self.matrix.clear()
            
            self.matrix.draw_text_layout(
                self.layout.name,
                "goal leaders",
                backgroundColor=(255,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.goal_leaders.get('data')[0].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.goal_leaders.get('data')[1].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.goal_leaders.get('data')[2].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.goal_leaders.get('data')[3].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.goal_leaders.get('data')[0].get('goals')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.goal_leaders.get('data')[1].get('goals')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.goal_leaders.get('data')[2].get('goals')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.goal_leaders.get('data')[3].get('goals')}"
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.assist_leaders:
            self.matrix.clear()
            
            self.matrix.draw_text_layout(
                self.layout.name,
                "assist leaders",
                backgroundColor=(255,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.assist_leaders.get('data')[0].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.assist_leaders.get('data')[1].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.assist_leaders.get('data')[2].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.assist_leaders.get('data')[3].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.assist_leaders.get('data')[0].get('assists')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.assist_leaders.get('data')[1].get('assists')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.assist_leaders.get('data')[2].get('assists')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.assist_leaders.get('data')[3].get('assists')}"
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.win_leaders:
            self.matrix.clear()
            
            self.matrix.draw_text_layout(
                self.layout.name,
                "win leaders",
                backgroundColor=(255, 0, 0)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.win_leaders.get('data')[0].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.win_leaders.get('data')[1].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.win_leaders.get('data')[2].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.win_leaders.get('data')[3].get('lastName').lower()}",
                fillColor=(255, 173, 51)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.win_leaders.get('data')[0].get('wins')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.win_leaders.get('data')[1].get('wins')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.win_leaders.get('data')[2].get('wins')}"
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.win_leaders.get('data')[3].get('wins')}"
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
