"""
    Show a summary of the favorite team. (previous game, next game, stats,)

"""
from PIL import Image, ImageFont, ImageDraw, ImageOps
from rgbmatrix import graphics
import nhl_api
from data.scoreboard import Scoreboard
from data.team import Team
from time import sleep
from utils import convert_date_format, get_file
from renderer.logos import LogoRenderer

class TeamSummary:
    def __init__(self, data, matrix,sleepEvent):
        '''
            TODO:
                Need to move the Previous/Next game info in the data section. I think loading it in the data section
                and then taking that info here would make sense
        '''
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors

        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('team_summary')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

    def render(self):
        for team_id in self.preferred_teams:
            self.team_id = team_id

            team = self.teams_info[team_id]
            team_data = Team(
                team.team_id,
                team.abbreviation,
                team.name
            )

            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))
            prev_game = team.previous_game
            next_game = team.next_game

            logo_renderer = LogoRenderer(
                self.matrix,
                self.data.config,
                self.layout.logo,
                team_data,
                'team_summary'
            )

            try:
                if prev_game:
                    prev_game_id = self.teams_info[team_id].previous_game.dates[0]["games"][0]["gamePk"]
                    prev_game_scoreboard = Scoreboard(nhl_api.overview(prev_game_id), self.data)
                else:
                    prev_game_scoreboard = False

                self.data.network_issues = False
            except ValueError:
                prev_game_scoreboard = False
                self.data.network_issues = True

            try:
                if next_game:
                    next_game_id = self.teams_info[team_id].next_game.dates[0]["games"][0]["gamePk"]
                    next_game_scoreboard = Scoreboard(nhl_api.overview(next_game_id), self.data)
                else:
                    next_game_scoreboard = False

                self.data.network_issues = False
            except ValueError:
                next_game_scoreboard = False
                self.data.network_issues = True

            stats = team.stats
            im_height = 67
            team_abbrev = team.abbreviation
            team_logo = Image.open(get_file('assets/logos/{}.png'.format(team_abbrev)))

            i = 0

            if not self.sleepEvent.is_set():
                image = self.draw_team_summary(
                    stats,
                    prev_game_scoreboard,
                    next_game_scoreboard,
                    bg_color,
                    txt_color,
                    im_height
                )
                self.matrix.clear()

                logo_renderer.render()

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image,
                )
                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

            self.sleepEvent.wait(5)

            # Move the image up until we hit the bottom.
            while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                i -= 1

                self.matrix.clear()

                logo_renderer.render()
                self.matrix.draw_image_layout(
                self.layout.info,
                image,
                (0, i)
                )

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                self.sleepEvent.wait(0.3)

            # Show the bottom before we change to the next table.
            self.sleepEvent.wait(5)

    def draw_team_summary(self, stats, prev_game_scoreboard, next_game_scoreboard, bg_color, txt_color, im_height):
        image = Image.new('RGB', (41, im_height))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 6, 26, -1], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 0), "RECORD:".format(), fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                font=self.font)
        if stats:
            draw.text((0, 7), "GP:{} P:{}".format(stats.gamesPlayed, stats.pts), fill=(255, 255, 255),
                font=self.font)
            draw.text((0, 13), "{}-{}-{}".format(stats.wins, stats.losses, stats.ot), fill=(255, 255, 255),
                font=self.font)
        else:
            draw.text((1, 7), "--------", fill=(200, 200, 200), font=self.font)

        draw.rectangle([0, 27, 36, 21], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 21), "LAST GAME:", fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                font=self.font)
        if prev_game_scoreboard:
            if prev_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 28), "@ {}".format(prev_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                        font=self.font)
            if prev_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 28), "VS {}".format(prev_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                        font=self.font)

            if self.data.status.is_irregular(prev_game_scoreboard.status):
                draw.text((0, 34), prev_game_scoreboard.status, fill=(255, 0, 0), font=self.font)

            else:
                if prev_game_scoreboard.winning_team == self.team_id:
                    draw.text((0, 34), "W", fill=(50, 255, 50), font=self.font)
                    draw.text((5, 34), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                        prev_game_scoreboard.home_team.goals),
                            fill=(255, 255, 255), font=self.font)

                if prev_game_scoreboard.loosing_team == self.team_id:
                    draw.text((0, 34), "L", fill=(255, 50, 50), font=self.font)
                    draw.text((5, 34), "{}-{}".format(prev_game_scoreboard.away_team.goals,
                                                        prev_game_scoreboard.home_team.goals),
                            fill=(255, 255, 255), font=self.font)

        else:
            draw.text((1, 27), "--------", fill=(200, 200, 200), font=self.font)

        draw.rectangle([0, 48, 36, 42], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, 42), "NEXT GAME:", fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                font=self.font)

        if next_game_scoreboard:
            date = convert_date_format(next_game_scoreboard.date)
            draw.text((0, 49), "{}".format(date.upper()), fill=(255, 255, 255), font=self.font)

            if self.data.status.is_irregular(next_game_scoreboard.status):
                if next_game_scoreboard.status == "Scheduled (Time TBD)":
                    next_game_scoreboard.status = "TBD"
                draw.text((0, 55), "{}".format(next_game_scoreboard.status.upper()), fill=(255, 0, 0), font=self.font)
            else:
                draw.text((0, 55), "{}".format(next_game_scoreboard.start_time), fill=(255, 255, 255), font=self.font)


            if next_game_scoreboard.away_team.id == self.team_id:
                draw.text((0, 61), "@ {}".format(next_game_scoreboard.home_team.abbrev), fill=(255, 255, 255),
                        font=self.font)
            if next_game_scoreboard.home_team.id == self.team_id:
                draw.text((0, 61), "VS {}".format(next_game_scoreboard.away_team.abbrev), fill=(255, 255, 255),
                        font=self.font)
        else:
            draw.text((1, 52), "--------", fill=(200, 200, 200), font=self.font)

        return image
