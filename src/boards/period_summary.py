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

class PeriodSummary:
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
        self.overview = nhl_api.overview(2022010056)
        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('team_summary')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        print("OVERVIEW")
        print(self.overview.home_team_name)

    def render(self):
        self.matrix.clear()
        for team_id in self.preferred_teams:
            self.team_id = team_id

            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))

            im_height = 67

            i = 0

            if not self.sleepEvent.is_set():
                image = self.draw_team_summary(
                    bg_color,
                    txt_color,
                    im_height
                )
                self.matrix.clear()

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
    def draw_team_summary(self, bg_color, txt_color, im_height):
        image = Image.new('RGB', (64, im_height))
        draw = ImageDraw.Draw(image)
        # draw.rectangle([0, 6, 100, -1], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        awayTeamStats = self.overview.boxscore['teams']['away']['teamStats']['teamSkaterStats']
        homeTeamStats = self.overview.boxscore['teams']['home']['teamStats']['teamSkaterStats']
        draw.text((1, 1), self.overview.away_team_abrev, fill=(255, 255, 255), font=self.font)
        draw.text((52, 1), self.overview.home_team_abrev, fill=(255,255,255), font=self.font)
        
        draw.text((19, 0), "2nd END".format(), fill=(txt_color['r'], txt_color['g'], txt_color['b']), font=self.font)

        draw.text((24, 7), f"{self.overview.away_score} - {self.overview.home_score}", fill=(255, 255, 255), font=self.font)
        away_sog = awayTeamStats['shots']
        home_sog = homeTeamStats['shots']
        draw.text((14, 14), f"{away_sog}  SOG  {home_sog}", fill=(255, 255, 255), font=self.font)
        home_pp = f"{int(homeTeamStats['powerPlayGoals'])}/{int(homeTeamStats['powerPlayOpportunities'])}"
        away_pp = f"{int(awayTeamStats['powerPlayGoals'])}/{int(awayTeamStats['powerPlayOpportunities'])}"
        draw.text((13, 21), f"{away_pp}  PP  {home_pp}", fill=(255, 255, 255), font=self.font)
        away_hits = awayTeamStats['hits']
        home_hits = homeTeamStats['hits']
        draw.text((13, 28), f"{away_hits}  HITS  {home_hits}", fill=(255, 255, 255), font=self.font)

        away_fo = awayTeamStats['faceOffWinPercentage']
        home_fo = homeTeamStats['faceOffWinPercentage']
        draw.text((10, 35), f"{away_fo}  FO%  {home_fo}", fill=(255, 255, 255), font=self.font)

        away_pim = awayTeamStats['pim']
        home_pim = homeTeamStats['pim']
        draw.text((14, 42), f"{away_pim}  PIM  {home_pim}", fill=(255, 255, 255), font=self.font)

        



        # draw.text((18, 35), "SCORERS", fill=(255, 255, 255), font=self.font)
        # draw.text((26, 42), "1st", fill=(255, 255, 255), font=self.font)
        # draw.text((16, 49), "8:47  (PP)", fill=(255, 255, 255), font=self.font)
        # # draw.text((5, 56), "L.Draisaitl (45)", fill=(255, 255, 255), font=self.font)
        # # draw.text((2, 56), "M.Zuccarello (13)", fill=(255, 255, 255), font=self.font)
        # draw.text((1, 56), "Marchessault (99)", fill=(255, 255, 255), font=self.font)
            
        return image
    # def draw_scorers(draw, )
