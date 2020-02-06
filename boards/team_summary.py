"""
    Show a summary of the favorite team. (previous game, next game, stats,)

"""
from PIL import Image, ImageFont, ImageDraw, ImageOps
from rgbmatrix import graphics
import nhl_api
from data.scoreboard import Scoreboard
from time import sleep
from utils import convert_date_format

class TeamSummary:
    def __init__(self, data, matrix):
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors
        self.layout = data.config.layout

    def render(self):
        for team_id in self.preferred_teams:
            self.team_id = team_id
            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))
            prev_game = self.teams_info[team_id].previous_game
            next_game = self.teams_info[team_id].next_game

            if prev_game:
                prev_game_id = self.teams_info[team_id].previous_game.dates[0]["games"][0]["gamePk"]
                prev_game_scoreboard = Scoreboard(nhl_api.overview(prev_game_id), self.teams_info)
            else:
                prev_game_scoreboard = False

            if next_game:
                next_game_id = self.teams_info[team_id].next_game.dates[0]["games"][0]["gamePk"]
                next_game_scoreboard = Scoreboard(nhl_api.overview(next_game_id), self.teams_info)
                print('Next game scoreboard')
            else:
                next_game_scoreboard = False

            stats = self.teams_info[team_id].stats
            im_height = 67
            team_abbrev = self.teams_info[team_id].abbreviation
            print(stats.gamesPlayed)
            print(team_abbrev)
            logo_coord = self.layout._get_summary_logo_coord(team_id)
            team_logo = Image.open('logos/{}.png'.format(team_abbrev))

            i = 0
            image = self.draw_team_summary(stats, prev_game_scoreboard, next_game_scoreboard, bg_color, txt_color,
                                           im_height, self.matrix.width, i)

            self.matrix.clear()
            self.matrix.draw_image((0, 0), image)
            self.matrix.draw_image((logo_coord["x"], logo_coord["y"]), team_logo.convert("RGB"))
            self.matrix.render()
            sleep(5)

            # Move the image up until we hit the bottom.
            while i > -(im_height - self.matrix.height):
                i -= 1
                image = self.draw_team_summary(stats, prev_game_scoreboard, next_game_scoreboard, bg_color, txt_color,
                                               im_height, self.matrix.width,
                                                i)

                self.matrix.clear()
                self.matrix.draw_image((0, 0), image)
                self.matrix.draw_image((logo_coord["x"], logo_coord["y"]), team_logo.convert("RGB"))
                self.matrix.render()
                sleep(0.3)
            # Show the bottom before we change to the next table.
            sleep(5)

    def draw_team_summary(self, stats, prev_game_scoreboard, next_game_scoreboard, bg_color, txt_color, im_height,
                          width, i):
        image = Image.new('RGB', (self.matrix.width, self.matrix.height))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 6 + i, 26, -1 + i], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 0 + i), "RECORD:".format(), fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                  font=self.layout.font)
        draw.text((0, 7 + i), "GP: {} P: {}".format(stats.gamesPlayed, stats.pts), fill=(255, 255, 255),
                  font=self.layout.font)
        draw.text((0, 13 + i), "{}-{}-{}".format(stats.wins, stats.losses, stats.ot), fill=(255, 255, 255),
                  font=self.layout.font)

        draw.rectangle([0, 27 + i, 36, 21 + i], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 21 + i), "LAST GAME:", fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                  font=self.layout.font)
        if prev_game_scoreboard:
            if prev_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 28 + i), "@ {}".format(prev_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                          font=self.layout.font)
            if prev_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 28 + i), "VS {}".format(prev_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                          font=self.layout.font)
            if prev_game_scoreboard.winning_team == self.team_id:
                draw.text((0, 34 + i), "W", fill=(50, 255, 50), font=self.layout.font)
                draw.text((5, 34 + i), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                      prev_game_scoreboard.home_team.goals),
                          fill=(255, 255, 255), font=self.layout.font)

            if prev_game_scoreboard.loosing_team == self.team_id:
                draw.text((0, 34 + i), "L", fill=(255, 50, 50), font=self.layout.font)
                draw.text((5, 34 + i), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                      prev_game_scoreboard.home_team.goals),
                          fill=(255, 255, 255), font=self.layout.font)

        else:
            draw.text((1, 27 + i), "--------", fill=(200, 200, 200), font=self.layout.font)

        draw.rectangle([0, 48 + i, 36, 42 + i], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 42 + i), "NEXT GAME:", fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                  font=self.layout.font)

        if next_game_scoreboard:
            date = convert_date_format(next_game_scoreboard.date)
            draw.text((0, 49 + i), "{}".format(date), fill=(255, 255, 255), font=self.layout.font)
            draw.text((0, 55 + i), "{}".format(next_game_scoreboard.start_time), fill=(255, 255, 255), font=self.layout.font)
            if next_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 61 + i), "@ {}".format(next_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                          font=self.layout.font)
            if next_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 61 + i), "VS {}".format(next_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                          font=self.layout.font)

        return image
