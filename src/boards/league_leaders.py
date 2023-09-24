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
        self.text = True
        self.image = Image.open(get_file('assets/images/stanley_cup.png'))
        self.sleepEvent.clear()
        self.draw_leaders()

    def draw_stanley_cup(self):
        if self.data.isPlayoff:
            if self.text:
                self.matrix.draw_text_layout(
                    self.layout.scp,
                    "SCP",
                    backgroundColor=(148, 148, 148),
                    fillColor=(0, 0, 0)
                )
            else:
                self.matrix.draw_image_layout(
                    self.layout.stanley_cup,
                    self.image
                )

    def draw_leaderboard(self, title, data, value_key, player_color, player_bg_color):
        if data:
            self.matrix.clear()
            self.draw_stanley_cup()

            self.matrix.draw_text_layout(
                self.layout.name,
                f"{self.playoff}{title}",
                backgroundColor=(0, 0, 0),
                fillColor=(239, 35, 60)
            )

            for i in range(4):
                player_data = data[i]
                player_name = player_data.get('lastName').lower()
                player_value = player_data.get(value_key)

                # Round the TOI values
                if value_key == 'timeOnIcePerGame':
                    player_value = round(player_value / 60, 1)

                self.matrix.draw_text_layout(
                    getattr(self.layout, f'player{i + 1}'),
                    player_name,
                    fillColor=player_color,
                    backgroundColor=(0, 0, 0)
                )

                self.matrix.draw_text_layout(
                    getattr(self.layout, f'points{i + 1}'),
                    str(player_value),
                    fillColor=(232, 232, 232),
                )

            self.matrix.render()
            self.sleepEvent.wait(10)

    def draw_leaders(self):
        if self.data.config.point_leaders:
            self.draw_leaderboard("point leaders", self.data.point_leaders.get('data'), 'points',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.goal_leaders:
            self.draw_leaderboard("goal leaders", self.data.goal_leaders.get('data'), 'goals',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.assist_leaders:
            self.draw_leaderboard("assist leaders", self.data.assist_leaders.get('data'), 'assists',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.win_leaders:
            self.draw_leaderboard("win leaders", self.data.win_leaders.get('data'), 'wins',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.plus_minus_leaders:
            self.draw_leaderboard("+/- leaders", self.data.plus_minus_leaders.get('data'), 'plusMinus',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.penalty_minute_leaders:
            self.draw_leaderboard("PIM leaders", self.data.penalty_minute_leaders.get('data'), 'penaltyMinutes',
                                  (251, 133, 0), (0, 0, 0))

        if self.data.config.time_on_ice_leaders:
            self.draw_leaderboard("TOI leaders", self.data.time_on_ice_leaders.get('data'), 'timeOnIcePerGame',
                                  (251, 133, 0), (0, 0, 0))
