from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format
from renderer.matrix import MatrixPixels
import debug

"""
    Show the details of a goal:
            - Time of the goal and which period
            - The players number, name and the team abbrev badge.
"""

class GoalRenderer:
    def __init__(self, data, matrix, sleepEvent, scoring_team):
        team = scoring_team
        goal_details = team.goal_plays[-1] # Get the last goal of the list of plays
        team_colors = data.config.team_colors
        self.period = goal_details.period
        self.periodTime = goal_details.periodTime
        self.teamAbbrev = team.abbrev
        self.scorer = goal_details.scorer
        self.assists = goal_details.assists
        self.rotation_rate = 10
        self.matrix = matrix
        self.font = data.config.layout.font
        self.font_medium = data.config.layout.font_medium
        self.layout = data.config.config.layout.get_board_layout('goal')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        self.team_bg_color = team_colors.color("{}.primary".format(team.id))
        self.team_txt_color = team_colors.color("{}.text".format(team.id))

    def render(self):
        debug.log("rendering goal detail board.")
        # Show the Scorer information 
        self.matrix.clear()
        self.draw_scorer()

        self.matrix.render()
        self.sleepEvent.wait(self.rotation_rate)

        #Show the Assists information
        self.matrix.clear()
        self.draw_details()

        self.matrix.render()
        self.sleepEvent.wait(self.rotation_rate)

    def draw_scorer(self):
        self.matrix.draw.rectangle([0,0,64,6], fill=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b']))
        self.matrix.draw_text(
                (1, 1), 
                "GOAL @ {}/{}".format(self.periodTime, self.period), 
                font=self.font, 
                fill=(self.team_txt_color['r'], self.team_txt_color['g'], self.team_txt_color['b'])
            )

        self.draw_hashtag()
        self.matrix.draw_text(
                (11, 8), 
                str(self.scorer["info"]["sweaterNumber"]),
                font=self.font_medium, 
                fill=(255,255,255)
            )
        
        # Drawing the Team Badge
        text_image = Image.new('RGBA', (13,7), (self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b'],255))
        draw_teambadge = ImageDraw.Draw(text_image)
        draw_teambadge.text((1,0), self.teamAbbrev, (self.team_txt_color['r'], self.team_txt_color['g'], self.team_txt_color['b'], 255), font=self.font)
        rotated_text_image = text_image.rotate(90, expand=True)
        self.matrix.image.paste(rotated_text_image,(0,19))

        self.matrix.draw_text(
                (8, 20), 
                self.scorer["info"]["firstName"]["default"].upper(),
                font=self.font, 
                fill=(255,255,255)
            )
        self.matrix.draw_text(
                (8, 26), 
                self.scorer["info"]["lastName"]["default"].upper(),
                font=self.font, 
                fill=(255,255,255)
            )

    def draw_details(self):
        self.matrix.draw.rectangle([0,0,64,6], fill=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b']))
        self.matrix.draw_text(
                (1, 1), 
                "GOAL @ {}/{}".format(self.periodTime, self.period), 
                font=self.font, 
                fill=(self.team_txt_color['r'], self.team_txt_color['g'], self.team_txt_color['b'])
            )

        scorer_name_coord = self.matrix.draw_text(
                (1, 8), 
                self.scorer["info"]["lastName"]["default"].upper(), 
                font=self.font, 
                fill=(255, 255, 255)
            )
        scorer_points_x_coord = scorer_name_coord["position"][0] + scorer_name_coord["size"][0] + 3
        self.matrix.draw_text(
                (scorer_points_x_coord, 8),
                "", # This was points in the game, but we don't get it. Should we do something else?
                font=self.font, 
                fill=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b'])
            )

        self.matrix.draw_text(
                (1, 15), 
                "ASSISTS", 
                font=self.font, 
                fill=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b']),
            )

        assists_y_pos = 21
        if self.assists:
            for i in range(len(self.assists)):
                assist_name_coord = self.matrix.draw_text(
                    (1, assists_y_pos), 
                    self.assists[i]["info"]["lastName"]["default"].upper(), 
                    font=self.font, 
                    fill=(255, 255, 255)
                )
                assists_points_x_coord = assist_name_coord["position"][0] + assist_name_coord["size"][0] + 3
                self.matrix.draw_text(
                    (assists_points_x_coord, assists_y_pos), 
                    "", # This was points in the game, but we don't get it. Should we do something else?
                    font=self.font, 
                    fill=(self.team_bg_color['r'], self.team_bg_color['g'], self.team_bg_color['b'])
                )
                assists_y_pos += 6
        else:
            self.matrix.draw_text(
                    (1, assists_y_pos), 
                    "UNASSISTED", 
                    font=self.font, 
                    fill=(255, 255, 255)
                )

    def draw_hashtag(self):
        """
            TODO: This function need to be coded a better way. but it works :D

            Carousel indicator.
        """
        hashtag_dots = [
            (3,0),(4,0),(7,0),(8,0),
            (3,1),(4,1),(7,1),(8,1),
            (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),
            (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),
            (2,4),(3,4),(6,4),(7,4),
            (2,5),(3,5),(6,5),(7,5),
            (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),
            (0,7),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),
            (1,8),(2,8),(5,8),(6,8),
            (1,9),(2,9),(5,9),(6,9)
            ]

        pixels = []

        # Render the indicator
        for dots_coord in range(len(hashtag_dots)):
            color = (255, 255, 255)
            pixels.append(
              MatrixPixels(
                hashtag_dots[dots_coord], 
                color
              )
            )

        self.matrix.draw_pixels_layout(
            self.layout.scorer_info.hashtag_dots,
            pixels,
            (10, 10)
        )