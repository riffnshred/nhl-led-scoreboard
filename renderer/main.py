from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
import time
import debug

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32

        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def render(self):
        # loop through the different state.
        while True:
            self.data.get_current_date()
            self.data.refresh_fav_team_status()
            # Fav team game day
            if self.data.fav_team_game_today:
                debug.info('Game day State')
                self.__render_game()
            # Fav team off day
            else:
                debug.info('Off day State')
                self.__render_off_day()

    def __render_game(self):

        if self.data.fav_team_game_today == 1:
            debug.info('Scheduled State')
            self._draw_pregame()
            time.sleep(1800)
        elif self.data.fav_team_game_today == 2:
            debug.info('Pre-Game State')
            self._draw_pregame()
            time.sleep(60)
        elif (self.data.fav_team_game_today == 3) or (self.data.fav_team_game_today == 4):
            debug.info('Live State')
            # Draw the current game
            self._draw_game()
        elif (self.data.fav_team_game_today == 5) or (self.data.fav_team_game_today == 6) or (self.data.fav_team_game_today == 7):
            debug.info('Final State')
            self._draw_post_game()
            #sleep an hour
            time.sleep(3600)
        debug.info('ping render_game')

    def __render_off_day(self):

        debug.info('ping_day_off')
        self._draw_off_day()
        time.sleep(21600) #sleep 6 hours

    def _draw_pregame(self):

        if self.data.get_schedule() != 0:

            overview = self.data.schedule

            # Save when the game start
            game_time = overview['game_time']

            # Center the game time on screen.
            game_time_pos = center_text(self.font_mini.getsize(game_time)[0], 32)

            # Set the position of each logo
            away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
            home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

            # Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
            home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

            # Draw the text on the Data image.
            self.draw.text((22, -1), 'TODAY', font=self.font_mini)
            self.draw.multiline_text((game_time_pos, 5), game_time, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 13), 'VS', font=self.font)

            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)

            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):
        self.data.refresh_overview()
        overview = self.data.overview
        home_score = overview['home_score']
        away_score = overview['away_score']

        while True:

            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game overview')
                self.data.refresh_overview()
                self.data.needs_refresh = False

            if self.data.overview != 0:
                overview = self.data.overview

                # Use This code if you want the goal animation to run only for your fav team's goal
                # if self.data.fav_team_id == overview['home_team_id']:
                #     if overview['home_score'] > home_score:
                #         self._draw_goal()
                # else:
                #     if overview['away_score'] > away_score:
                #         self._draw_goal()

                # Use this code if you want the goal animation to run for both team's goal.
                # Run the goal animation if there is a goal.
                if overview['home_score'] > home_score or overview['away_score'] > away_score:
                   self._draw_goal()

                # Prepare the data
                score = '{}-{}'.format(overview['away_score'], overview['home_score'])
                period = overview['period']
                time_period = overview['time']

                # Set the position of the information on screen.
                time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 32)
                score_position = center_text(self.font.getsize(score)[0], 32)
                period_position = center_text(self.font_mini.getsize(period)[0], 32)

                # Set the position of each logo on screen.
                away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
                home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

                # Open the logo image file
                away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
                home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

                # Draw the text on the Data image.
                self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
                self.draw.multiline_text((period_position, -1), period, fill=(255, 255, 255), font=self.font_mini, align="center")
                self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")

                # Put the data on the canvas
                self.canvas.SetImage(self.image, 0, 0)

                # Put the images on the canvas
                self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
                self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)

                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)


                # Check if the game is over
                if overview['game_status'] == 6 or overview['game_status'] == 7:
                    debug.info('GAME OVER')
                    break

                # Save the scores.
                away_score = overview['away_score']
                home_score = overview['home_score']

                self.data.needs_refresh = True
                time.sleep(60)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(60)  # sleep for 1 min

    def _draw_post_game(self):
        self.data.refresh_overview()
        if self.data.overview != 0:
            overview = self.data.overview

            # Prepare the data
            game_date = '{} {}'.format(month_abbr[self.data.month], self.data.day)
            score = '{}-{}'.format(overview['away_score'], overview['home_score'])
            period = overview['period']
            time_period = overview['time']

            # Set the position of the information on screen.
            game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 32)
            time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 32)
            score_position = center_text(self.font.getsize(score)[0], 32)

            # Draw the text on the Data image.
            self.draw.multiline_text((game_date_pos, -1), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
            self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")

            # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
            if period == "OT" or period == "SO":
                period_position = center_text(self.font_mini.getsize(period)[0], 32)
                self.draw.multiline_text((period_position, 11), period, fill=(255, 255, 255), font=self.font_mini,align="center")

            # Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
            home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

            # Set the position of each logo on screen.
            away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
            home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)

            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min

    def _draw_goal(self):

        debug.info('SCOOOOOOOORE, MAY DAY, MAY DAY, MAY DAY, MAY DAAAAAAAAY - Rick Jeanneret')
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