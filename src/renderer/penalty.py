from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format
from renderer.matrix import MatrixPixels
import debug
from nhl_api.info import TeamInfo

"""
    Show the details of a goal:
            - Time of the goal and which period
            - The players number, name and the team abbrev badge.
"""

class PenaltyRenderer:
    def __init__(self, data, matrix, sleepEvent, team):
        penalty_details = team.penalties[-1] # Get the last goal of the list of plays
        team_colors = data.config.team_colors
        team_id = penalty_details.team_id
        self.team: TeamInfo = data.teams_info[team_id]
        self.player = penalty_details.player
        self.periodTime = penalty_details.periodTime
        self.penaltyMinutes = penalty_details.penaltyMinutes # TODO: I don't know if we have this
        self.severity = penalty_details.severity
        self.rotation_rate = 10
        self.matrix = matrix
        self.font = data.config.layout.font
        self.font_medium = data.config.layout.font_medium
        self.layout = data.config.config.layout.get_board_layout('penalty')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        self.team_bg_color = team_colors.color("{}.primary".format(team_id))
        self.team_txt_color = team_colors.color("{}.text".format(team_id))

    def render(self):
        debug.log("rendering goal detail board.")
        # Show the Scorer information 
        self.matrix.clear()
        self.draw_penalty()
        

        self.matrix.render()
        self.sleepEvent.wait(self.rotation_rate)

    def draw_penalty(self):
        
        self.matrix.draw_text(
            (1, 1), 
            "Penalty @ {}".format(self.periodTime), 
            font=self.font, 
            fill=(0, 0, 0),
            backgroundColor=(255,195,12)
        )
        
        self.matrix.draw_text_layout(
            self.layout.team_name, 
            self.team.details.abbrev,
            fillColor=(self.team_txt_color['r'], self.team_txt_color['g'], self.team_txt_color['b']),
            backgroundColor=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b'])
        )
        
        self.draw_hashtag()

        self.matrix.draw_text_layout(
            self.layout.jersey_number, 
            str(self.player.sweater_number)
        )

        self.matrix.draw_text_layout(
            self.layout.last_name, 
            self.player.last_name.default
        )
        self.matrix.draw_text_layout(
            self.layout.minutes, 
            "{}:00".format(self.penaltyMinutes),
        )
        self.matrix.draw_text_layout(
            self.layout.severity, 
            self.severity, 
            fillColor=(255,195,12),
        )

    def draw_hashtag(self):
        hashtag_dots = [
            (2,0),(4,0),
            (1,1),(2,1),(3,1),(4,1),(5,1),
            (2,2),(4,2),
            (1,3),(2,3),(3,3),(4,3),(5,3),
            (2,4),(4,4),
            ]
        pixels = []

        for dots_coord in range(len(hashtag_dots)):
            color = (255, 255, 255)
            pixels.append(
              MatrixPixels(
                hashtag_dots[dots_coord], 
                color
              )
            )

        self.matrix.draw_pixels_layout(
            self.layout.hashtag_dots,
            pixels,
            (32, 10)
        )
