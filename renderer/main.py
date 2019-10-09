from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text_position
from renderer.screen_config import screenConfig
import time


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        self.image = Image.new('RGB', (self.width, self.height))

    def render(self):
        """
            This is where we call the different render modules
        """
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

        if self.data.fav_team_game_today:
            self.__render_game()
        else:
            self.__render_off_day()

    def __render_game(self):
        while True:
            print("In _render_game")
            if self.data.fav_team_game_today == "Preview":
                print('Preview State')
                self._draw_pregame()
            elif self.data.fav_team_game_today == "Pre-Game":
                print('Pre-Game State')
                self._draw_pregame()
            elif self.data.fav_team_game_today == "Live":
                print('Live State')
                # Draw the current game
                self._draw_game()
            elif self.data.fav_team_game_today == "Final":
                print('Final State')
                self._draw_game()

            print("ping render_game")

    def __render_off_day(self):
        while True:
            self._draw_off_day()

            time.sleep(21600) #sleep 6 hours
            print("ping_day_off")

    def _draw_pregame(self):
        if self.data.needs_refresh:
            print('check refresh')
            self.data.refresh_overview()
            self.data.needs_refresh = False
        if self.data.overview != 0:
            self.draw.text((0, 0), 'Game Will Start', font=self.font_mini)
            self.draw.text((0, 7), 'Soon', font=self.font_mini)
            self.canvas.SetImage(self.image, 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            self.data.needs_refresh = True
            time.sleep(60) #sleep for 1 min
        else:
            #If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min

    def _draw_game(self):
        self.data.refresh_overview()
        overview = self.data.overview
        home_score = overview['home_score']
        away_score = overview['away_score']


        while True:
            if self.data.needs_refresh:
                print('check refresh')
                self.data.refresh_overview()
                self.data.needs_refresh = False

            if self.data.overview != 0:
                overview = self.data.overview

                if overview['home_score'] > home_score or overview['away_score'] > away_score:
                    self._draw_goal()

                score = '{}-{}'.format(overview['away_score'], overview['home_score'])
                period = overview['period']
                time_period = overview['time']
                away_team_logo = 'logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation'])
                home_team_logo = 'logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation'])

                away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
                home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

                score_position = center_text_position(score,32,6)

                self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
                self.draw.text((26, -1), period, font=self.font_mini)
                self.draw.text((23, 5), time_period, font=self.font_mini)


                away_team_logo = Image.open(away_team_logo)
                home_team_logo = Image.open(home_team_logo)
                self.canvas.SetImage(self.image, 0, 0)
                self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
                self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(30)
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                away_score = overview['away_score']
                home_score = overview['home_score']
                self.data.needs_refresh = True
            else:
                # If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(60)  # sleep for 1 min

    def _draw_goal(self):
        # Load the gif file
        im = Image.open("Assets/goal_light_animation.gif")
        # Set the frame index to 0
        frameNo = 0

        self.canvas.Clear()

        # Go through the frames
        x = 0
        while x is not 5:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)

            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            time.sleep(0.1)

    def _draw_off_day(self):
        self.draw.text((0, -1), 'NO GAME TODAY', font=self.font_mini)
        self.canvas.SetImage(self.image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)