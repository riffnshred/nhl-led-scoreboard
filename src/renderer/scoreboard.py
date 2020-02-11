from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format
from renderer.logos import TeamLogos as LogoRenderer

class ScoreboardRenderer:
    def __init__(self, data, matrix, scoreboard):
        self.data = data
        self.status = data.status
        self.layout = self.data.config.layout
        self.font = self.layout.font
        self.font_large = self.layout.font_large
        self.scoreboard = scoreboard
        self.matrix = matrix

        self.home_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.scoreboard.home_team,
            "home"
        )
        self.away_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.scoreboard.away_team,
            "away"
        )

    def render(self):
        
        self.away_logo_renderer.render()
        self.home_logo_renderer.render()

        if self.status.is_scheduled(self.scoreboard.status):
            self.draw_scheduled()

        if self.status.is_live(self.scoreboard.status):
            self.draw_live()

        if self.status.is_final(self.scoreboard.status):
            self.draw_final()

        if self.status.is_irregular(self.scoreboard.status):
            '''TODO: Need to figure out the irregular status'''
            pass

    def draw_scheduled(self):
        start_time = self.scoreboard.start_time

        # Draw the text on the Data image.
        self.matrix.draw_text((0, -1), 'TODAY', font=self.layout.font, location="center")
        self.matrix.draw_text(
            (0, 5), start_time, fill=(255, 255, 255), location="center", 
            font=self.font, align="center", multiline=True
        )
        self.matrix.draw_text((0, 13), 'VS', font=self.font_large, location="center")

    def draw_live(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        clock = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        SOG = '{}-{}'.format(self.scoreboard.away_team.shot_on_goal, self.scoreboard.home_team.shot_on_goal)

        # Draw the info
        self.matrix.draw_text(
            (0, -1), period, fill=(255, 255, 255), location="center",
            font=self.font, align="center", multiline=True
        )
        self.matrix.draw_text(
            (0, 5), clock, fill=(255, 255, 255), location="center", 
            font=self.font, align="center", multiline=True
        )
        self.matrix.draw_text(
            (0, 15), score, fill=(255, 255, 255), location="center", 
            font=self.font_large, align="center", multiline=True
        )

    def draw_final(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        result = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        date = convert_date_format(self.scoreboard.date)

        # Align the into with center of screen
        date_align = center_text(self.font.getsize(date)[0], 32)
        score_align = center_text(self.font_large.getsize(score)[0], 32)

        # Draw the info
        self.matrix.draw_text(
            (0, -1), date, fill=(255, 255, 255), location="center", 
            font=self.font, align="center", multiline=True
        )
        if self.scoreboard.periods.number > 3:
            self.matrix.draw_text(
                (0, 5), "F/{}".format(period), fill=(255, 255, 255), location="center", 
                font=self.font, align="center", multiline=True
            )
        else:
            self.matrix.draw_text(
                (0, 5), result, fill=(255, 255, 255), location="center", 
                font=self.font, align="center", multiline=True
            )

        self.matrix.draw_text(
            (0, 15), score, fill=(255, 255, 255), location="center", 
            font=self.font_large, align="center", multiline=True
        )

    def draw_Irregular(self):
        pass
