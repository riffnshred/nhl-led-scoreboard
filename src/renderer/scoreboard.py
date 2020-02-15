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
            self.layout,
            self.scoreboard.home_team,
            "home"
        )
        self.away_logo_renderer = LogoRenderer(
            self.matrix,
            self.layout,
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
        self.matrix.render()


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

        self.matrix.render()
        if (self.scoreboard.away_team.num_skaters < 5) or (self.scoreboard.home_team.num_skaters < 5):
            print("hello")
            self.draw_power_play()
        if self.scoreboard.intermission:
            self.draw_end_period_indicator()

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
        self.matrix.render()
        self.draw_end_period_indicator()

    def draw_irregular(self):
        pass

    def draw_power_play(self):
        away_number_skaters = self.scoreboard.away_team.num_skaters
        home_number_skaters = self.scoreboard.home_team.num_skaters
        yellow = self.matrix.graphics.Color(255, 255, 0)
        red = self.matrix.graphics.Color(255, 0, 0)
        green = self.matrix.graphics.Color(0, 255, 0)
        colors = {"6": green, "5": green, "4": yellow, "3": red}

        self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 1, 3, self.matrix.height - 1,
                                      colors[str(away_number_skaters)])
        self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 2, 1, self.matrix.height - 2,
                                      colors[str(away_number_skaters)])
        self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 3, 0, self.matrix.height - 3,
                                      colors[str(away_number_skaters)])

        self.matrix.graphics.DrawLine(self.matrix.matrix, 63, self.matrix.height - 1, 60,
                                      self.matrix.height - 1, colors[str(home_number_skaters)])
        self.matrix.graphics.DrawLine(self.matrix.matrix, 63, self.matrix.height - 2, 62,
                                      self.matrix.height - 2, colors[str(home_number_skaters)])
        self.matrix.graphics.DrawLine(self.matrix.matrix, 63, self.matrix.height - 3, 63,
                                      self.matrix.height - 3, colors[str(home_number_skaters)])


    def draw_end_period_indicator(self):
        """TODO: change the width depending how much time is left to the intermission"""
        color = self.matrix.graphics.Color(0, 255, 0)
        self.matrix.graphics.DrawLine(self.matrix.matrix, 23, self.matrix.height - 2, 39, self.matrix.height - 2, color)
        self.matrix.graphics.DrawLine(self.matrix.matrix, 22, self.matrix.height - 1, 40, self.matrix.height - 1,
                                      color)