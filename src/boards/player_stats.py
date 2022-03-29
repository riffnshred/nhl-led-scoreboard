from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
import re
import debug
from time import sleep
from utils import center_text, get_file
from data.data import Data


class PlayerStats:
    def __init__(self, data, matrix, sleepEvent ,duration=None):

        
        self.matrix = matrix
        self.data = data

        self.layout = self.data.config.config.layout.get_board_layout('player_stats')
        self.image = Image.open(get_file('assets/images/hashtag.png'))
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.font = data.config.layout.font



            #sleep(1)
        self.draw_stats()

        self.sleepEvent.wait(15)



    def draw_stats(self):
        self.matrix.clear()
        self.matrix.draw_text_layout(
            self.layout.goals_num,
            str(self.data.favorite_player_stats.json()["stats"][0]["splits"][0]["stat"]["goals"]),
            fillColor=(30,144,255)
        )
        self.matrix.draw_text_layout(
            self.layout.assists_num,
            str(self.data.favorite_player_stats.json()["stats"][0]["splits"][0]["stat"]["assists"]),
            fillColor=(255, 73, 56)
        )
        self.matrix.draw_text_layout(
            self.layout.name,
            self.data.favorite_player_data.json()["people"][0]["lastName"].upper()

        )

        self.matrix.draw_image_layout(
            self.layout.hashtag,
            self.image
        )
        self.matrix.draw_text_layout(
            self.layout.number,
            self.data.favorite_player_data.json()["people"][0]["primaryNumber"]

        )
        self.matrix.draw_text_layout(
            self.layout.goals,
            "GOALS",
            fillColor=(30,144,255)

        )   
        self.matrix.draw_text_layout(
            self.layout.assists,
            "APPLES",
            fillColor=(255, 73, 56)

        )   

        # Display curr temp and humidity on clock, bottom
       
        self.matrix.render()
