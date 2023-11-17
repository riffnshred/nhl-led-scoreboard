from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format, get_file
from renderer.logos import LogoRenderer
from data.scoreboard import Scoreboard

class ScoreboardRenderer:
    def __init__(self, data, matrix, scoreboard: Scoreboard, shot_on_goal=False):
        self.data = data
        self.status = data.status
        self.layout = self.data.config.config.layout.get_board_layout('scoreboard')
        self.font = self.data.config.layout.font
        self.font_large = self.data.config.layout.font_large
        self.team_colors = data.config.team_colors
        self.scoreboard = scoreboard
        self.matrix = matrix
        self.show_SOG = shot_on_goal

        self.home_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.layout.home_logo,
            self.scoreboard.home_team.abbrev,
            'scoreboard',
            'home'
        )
        self.away_logo_renderer = LogoRenderer(
            self.matrix,
            data.config,
            self.layout.away_logo,
            self.scoreboard.away_team.abbrev,
            'scoreboard',
            'away'
        )

    def render(self):
        self.matrix.clear()
        # bg_away = self.team_colors.color("{}.primary".format(self.scoreboard.away_team.id))
        # bg_home = self.team_colors.color("{}.primary".format(self.scoreboard.home_team.id))
        # self.matrix.draw_rectangle((0,0), (64,64), (bg_away['r'],bg_away['g'],bg_away['b']))
        # self.matrix.draw_rectangle((64,0), (128,64), (bg_home['r'],bg_home['g'],bg_home['b']))
        display_width = self.matrix.width
        display_height = self.matrix.height

        self.matrix.draw_rectangle((0,0), ((display_width/2),display_height), (0,0,0))
        self.away_logo_renderer.render()

        self.matrix.draw_rectangle(((display_width/2),0), ((display_width),display_height), (0,0,0))
        self.home_logo_renderer.render()
        
        gradient = Image.open(get_file('assets/images/64x32_scoreboard_center_gradient.png'))

        # For 128x64 use the bigger gradient image.
        if display_height == 64:
            gradient = Image.open(get_file('assets/images/128x64_scoreboard_center_gradient.png'))
        
        self.matrix.draw_image((display_width/2,0), gradient, align="center")
        
        if self.status.is_scheduled(self.scoreboard.status):
            self.draw_scheduled()

        if self.status.is_live(self.scoreboard.status):
            self.draw_live()

        if self.status.is_game_over(self.scoreboard.status):
            self.draw_final()

        if self.status.is_final(self.scoreboard.status):
            self.draw_final()

        if self.status.is_irregular(self.scoreboard.status):
            '''TODO: Need to figure out the irregular status'''
            self.draw_irregular()

    def draw_scheduled(self):
        start_time = self.scoreboard.start_time

        # Draw the text on the Data image.
        self.matrix.draw_text_layout(
          self.layout.scheduled_date, 
          'TODAY'
        )
        self.matrix.draw_text_layout(
          self.layout.scheduled_time, 
          start_time
        )

        self.matrix.draw_text_layout(
          self.layout.vs, 
          'VS'
        )


        self.matrix.render()

    def draw_live(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        clock = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        

        if self.show_SOG:
            self.draw_SOG()
            self.show_SOG = False
        else:
            # Draw the info
            self.matrix.draw_text_layout(
                self.layout.period,
                period,
            )
            self.matrix.draw_text_layout(
                self.layout.clock,
                clock
            )

        self.matrix.draw_text_layout(
            self.layout.score,
            score
        )

        self.matrix.render()
        if self.scoreboard.away_team.powerplay or self.scoreboard.home_team.powerplay:
            self.draw_power_play()


    def draw_final(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        result = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)

        # Draw the info
        self.matrix.draw_text_layout(
            self.layout.center_top, 
            str(self.scoreboard.date)
        )

        end_text = result
        if self.scoreboard.periods.number > 3:
            end_text = "F/{}".format(period)

        self.matrix.draw_text_layout(
            self.layout.period_final, 
            end_text
        )

        self.matrix.draw_text_layout(
            self.layout.score, 
            score
        )

        self.matrix.render()

    def draw_irregular(self):
        status = self.scoreboard.status
        if status == "Postponed":
            status = "PPD"

        # Draw the text on the Data image.
        self.matrix.draw_text_layout(
            self.layout.center_top,
            'TODAY'
        )
        self.matrix.draw_text_layout(
            self.layout.irregular_status,
            status
        )
        self.matrix.draw_text_layout(
            self.layout.vs,
            'VS'
        )
        self.matrix.render()

    def draw_power_play(self):
        away_number_skaters = self.scoreboard.away_team.num_skaters
        home_number_skaters = self.scoreboard.home_team.num_skaters
        # yellow = self.matrix.graphics.Color(255, 255, 0)
        yellow = (255, 255, 0)
        # red = self.matrix.graphics.Color(255, 0, 0)
        red = (255, 0, 0)
        # green = self.matrix.graphics.Color(0, 255, 0)
        green = (0, 255, 0)
        colors = {"6": green, "5": green, "4": yellow, "3": red}

        # import pdb; pdb.set_trace()
        self.matrix.draw.line((0, self.matrix.height - 1, 3, self.matrix.height - 1), fill=colors[str(away_number_skaters)])
        # self.matrix.draw.line(((self.matrix.width * .5) - 9, self.matrix.height - 1, (self.matrix.width * .5) + 9, self.matrix.height - 1), fill=255)
        # self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 1, 3, self.matrix.height - 1, colors[str(away_number_skaters)])
        self.matrix.draw.line((0, self.matrix.height - 2, 1, self.matrix.height - 2), fill=colors[str(away_number_skaters)])
        # self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 2, 1, self.matrix.height - 2, colors[str(away_number_skaters)])
        self.matrix.draw.line((0, self.matrix.height - 3, 0, self.matrix.height - 3), fill=colors[str(away_number_skaters)])
        # self.matrix.graphics.DrawLine(self.matrix.matrix, 0, self.matrix.height - 3, 0, self.matrix.height - 3, colors[str(away_number_skaters)])
        self.matrix.draw.line((self.matrix.width - 1, self.matrix.height - 1, self.matrix.width - 4, self.matrix.height - 1), fill=colors[str(home_number_skaters)])
        # self.matrix.graphics.DrawLine(self.matrix.matrix, self.matrix.width - 1, self.matrix.height - 1, self.matrix.width - 4, self.matrix.height - 1, colors[str(home_number_skaters)])
        self.matrix.draw.line((self.matrix.width - 1, self.matrix.height - 2, self.matrix.width - 2, self.matrix.height - 2), fill=colors[str(home_number_skaters)])
        # self.matrix.graphics.DrawLine(self.matrix.matrix, self.matrix.width - 1, self.matrix.height - 2, self.matrix.width - 2, self.matrix.height - 2, colors[str(home_number_skaters)])
        self.matrix.draw.line((self.matrix.width - 1, self.matrix.height - 3, self.matrix.width - 1, self.matrix.height - 3), fill=colors[str(home_number_skaters)])
        # self.matrix.graphics.DrawLine(self.matrix.matrix, self.matrix.width - 1, self.matrix.height - 3, self.matrix.width - 1, self.matrix.height - 3, colors[str(home_number_skaters)])
        self.matrix.render()

    def draw_SOG(self):

        # Draw the Shot on goal
        SOG = '{}-{}'.format(self.scoreboard.away_team.shot_on_goal, self.scoreboard.home_team.shot_on_goal)
        
        self.matrix.draw_text_layout(
            self.layout.SOG_label,
            "SHOTS"
        )
        self.matrix.draw_text_layout(
            self.layout.SOG,
            SOG
        )
