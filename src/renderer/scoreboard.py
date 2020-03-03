from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format
from renderer.logos import LogoRenderer


class ScoreboardRenderer:
    def __init__(self, data, matrix, scoreboard, shot_on_goal=False):
        self.data = data
        self.status = data.status
        self.layout = self.data.config.config.layout.get_board_layout('scoreboard')
        self.font = self.data.config.layout.font
        self.font_large = self.data.config.layout.font_large
        self.scoreboard = scoreboard
        self.matrix = matrix
        self.show_sog = shot_on_goal

        self.home_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.layout.home_logo,
            self.scoreboard.home_team,
            'scoreboard',
            'home'
        )
        self.away_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.layout.away_logo,
            self.scoreboard.away_team,
            'scoreboard',
            'away'
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
        self.matrix.draw_text_layout(
          self.layout.scheduled_date, 
          'TODAY', 
          font=self.font
        )
        self.matrix.draw_text_layout(
          self.layout.scheduled_time, 
          start_time,
          font=self.font, 
          multiline=True
        )
        self.matrix.draw_text_layout(
          self.layout.vs, 
          'VS', 
          font=self.font_large
        )

        self.matrix.render()

    def draw_live(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        clock = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        SOG = '{}-{}'.format(self.scoreboard.away_team.shot_on_goal, self.scoreboard.home_team.shot_on_goal)

        # Draw the info
        self.matrix.draw_text_layout(
            self.layout.period,
            period,
            font=self.font, 
            multiline=True
        )
        self.matrix.draw_text_layout(
            self.layout.clock,
            clock,
            font=self.font,
            multiline=True
        )
        self.matrix.draw_text_layout(
            self.layout.score,
            score,
            font=self.font_large,
            multiline=True
        )

        self.matrix.render()
        if (3 <= self.scoreboard.away_team.num_skaters <= 4) or (3 <= self.scoreboard.home_team.num_skaters <= 4):
            self.draw_power_play()


    def draw_final(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        result = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        date = convert_date_format(self.scoreboard.date)

        # Draw the info
        self.matrix.draw_text_layout(
            self.layout.scheduled_date, 
            date,
            font=self.font,
            multiline=True
        )

        end_text = result
        if self.scoreboard.periods.number > 3:
            end_text = "F/{}".format(period)

        self.matrix.draw_text_layout(
            self.layout.period_final, 
            end_text,
            font=self.font,
            multiline=True
        )

        self.matrix.draw_text_layout(
            self.layout.score, 
            score,
            font=self.font_large,
            multiline=True
        )

        self.matrix.render()

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
