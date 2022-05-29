from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
import re
import debug
from time import sleep
from utils import center_text, get_file



class Leaders:
    def __init__(self, data, matrix, sleepEvent):

        self.data = data
        
        self.matrix = matrix
        self.layout = self.data.config.config.layout.get_board_layout('league_leaders')
        self.sleepEvent = sleepEvent
        self.playoff = ""
        self.image = Image.open(get_file('assets/images/stanley_cup.png'))
        self.sleepEvent.clear()
        self.draw_leaders()

    def draw_leaders(self):
        self.matrix.clear()


        self.backgroundColor = (0 , 0, 0)
        self.playerNameColor = (251, 133, 0)
        self.pointsColor = (232, 232, 232)
        if self.data.config.point_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )

            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}point leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)

            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.point_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.point_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.point_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.point_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.point_leaders.get('data')[0].get('points')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.point_leaders.get('data')[1].get('points')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.point_leaders.get('data')[2].get('points')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.point_leaders.get('data')[3].get('points')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.goal_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}goal leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.goal_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.goal_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.goal_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.goal_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.goal_leaders.get('data')[0].get('goals')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.goal_leaders.get('data')[1].get('goals')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.goal_leaders.get('data')[2].get('goals')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.goal_leaders.get('data')[3].get('goals')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.assist_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:   
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}assist leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.assist_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.assist_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.assist_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.assist_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.assist_leaders.get('data')[0].get('assists')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.assist_leaders.get('data')[1].get('assists')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.assist_leaders.get('data')[2].get('assists')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.assist_leaders.get('data')[3].get('assists')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.win_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}win leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.win_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.win_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.win_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.win_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.win_leaders.get('data')[0].get('wins')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.win_leaders.get('data')[1].get('wins')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.win_leaders.get('data')[2].get('wins')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.win_leaders.get('data')[3].get('wins')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        if self.data.config.plus_minus_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}+/- leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.plus_minus_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.plus_minus_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.plus_minus_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.plus_minus_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.plus_minus_leaders.get('data')[0].get('plusMinus')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.plus_minus_leaders.get('data')[1].get('plusMinus')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.plus_minus_leaders.get('data')[2].get('plusMinus')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.plus_minus_leaders.get('data')[3].get('plusMinus')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        
        if self.data.config.penalty_minute_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}PIM leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.penalty_minute_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.penalty_minute_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.penalty_minute_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.penalty_minute_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{self.data.penalty_minute_leaders.get('data')[0].get('penaltyMinutes')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{self.data.penalty_minute_leaders.get('data')[1].get('penaltyMinutes')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{self.data.penalty_minute_leaders.get('data')[2].get('penaltyMinutes')}",
                fillColor = self.pointsColor
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{self.data.penalty_minute_leaders.get('data')[3].get('penaltyMinutes')}",
                fillColor = self.pointsColor
            )
            self.matrix.render()
            self.sleepEvent.wait(10)

        if self.data.config.time_on_ice_leaders:
            self.matrix.clear()
            if self.data.isPlayoff:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )
            
            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}TOI leaders",
                backgroundColor=self.backgroundColor,
                fillColor=(239, 35, 60)
            )
            self.matrix.draw_text_layout(
                self.layout.player1,
                f"{self.data.time_on_ice_leaders.get('data')[0].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player2,
                f"{self.data.time_on_ice_leaders.get('data')[1].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player3,
                f"{self.data.time_on_ice_leaders.get('data')[2].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.player4,
                f"{self.data.time_on_ice_leaders.get('data')[3].get('lastName').lower()}",
                fillColor = self.playerNameColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points1,
                f"{round(self.data.time_on_ice_leaders.get('data')[0].get('timeOnIcePerGame')/60, 1)}",
                fillColor = self.pointsColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points2,
                f"{round(self.data.time_on_ice_leaders.get('data')[1].get('timeOnIcePerGame')/60, 1)}",
                fillColor = self.pointsColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points3,
                f"{round(self.data.time_on_ice_leaders.get('data')[2].get('timeOnIcePerGame')/60, 1)}",
                fillColor = self.pointsColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.draw_text_layout(
                self.layout.points4,
                f"{round(self.data.time_on_ice_leaders.get('data')[3].get('timeOnIcePerGame')/60, 1)}",
                fillColor = self.pointsColor,
                backgroundColor = (0,0,0)
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
