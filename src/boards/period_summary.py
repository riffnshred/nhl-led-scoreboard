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
                Clean up
                Add color
                rename stuff from the team summary board 
                only show after game + after periods
                loop thru all favorite teams
        '''
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors
        #Do not forget to change this \/
        self.overview = nhl_api.overview(2022010065) #this is just so I could use any game overview, CHANGE LATER!!!!!!!!!
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #self.data.overview
        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('team_summary')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        print("OVERVIEW")
        print(self.overview.home_team_name)
        self.away_color = self.team_colors.color("{}.primary".format(self.overview.away_team_id))
        self.home_color = self.team_colors.color("{}.primary".format(self.overview.home_team_id))
        print('PLAYS')
        print(self.overview.plays['scoringPlays'])

    def render(self):
        self.matrix.clear()
        for team_id in self.preferred_teams:
            self.team_id = team_id



            im_height = 56

            i = 0

            if not self.sleepEvent.is_set():
                image = self.draw_period_summary(
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
    def draw_period_summary(self, im_height):
        image = Image.new('RGB', (64, im_height))
        draw = ImageDraw.Draw(image)
        
        awayTeamStats = self.overview.boxscore['teams']['away']['teamStats']['teamSkaterStats']
        homeTeamStats = self.overview.boxscore['teams']['home']['teamStats']['teamSkaterStats']
        draw.text((1, 1), self.overview.away_team_abrev, fill=(self.away_color['r'], self.away_color['g'],self.away_color['b']), font=self.font)
        draw.text((52, 1), self.overview.home_team_abrev, fill=(self.home_color['r'], self.home_color['g'],self.home_color['b']), font=self.font)
        
        #!!!
        draw.text((19, 0), "2nd END".format(), fill=(255,255,255), font=self.font) #GET THIS TO ACTUALLY WORK
        #!!!

        # score
        draw.text((27, 8), f"{self.overview.away_score}", fill=(255, 255, 255), font=self.font, anchor='rt')
        draw.text((37, 7), f"{self.overview.home_score}", fill=(255, 255, 255), font=self.font)
        draw.text((30, 7), f"-", fill=(255, 255, 255), font=self.font)

        # SHOTS
        away_sog = awayTeamStats['shots']
        home_sog = homeTeamStats['shots']
        draw.text((26, 14), f"SOG", fill=(255, 255, 255), font=self.font)
        draw.text((19, 15), f"{away_sog}", fill=(255, 255, 255), font=self.font, anchor='rt')
        draw.text((43, 14), f"{home_sog}", fill=(255, 255, 255), font=self.font)


        # PP
        away_pp = f"{int(awayTeamStats['powerPlayGoals'])}/{int(awayTeamStats['powerPlayOpportunities'])}"
        home_pp = f"{int(homeTeamStats['powerPlayGoals'])}/{int(homeTeamStats['powerPlayOpportunities'])}"
        draw.text((19, 22), away_pp, fill=(255, 255, 255), font=self.font, anchor='rt')  
        draw.text((43, 21), home_pp, fill=(255, 255, 255), font=self.font)
        draw.text((28, 21), f"PP", fill=(255, 255, 255), font=self.font)

        #HITS
        away_hits = str(awayTeamStats['hits'])
        home_hits = str(homeTeamStats['hits'])
        draw.text((25, 28), f"HITS", fill=(255, 255, 255), font=self.font)
        draw.text((19, 29), away_hits, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 28), home_hits, fill=(255,255,255), font=self.font)


        # FO%
        away_fo = str(awayTeamStats['faceOffWinPercentage'])
        home_fo = str(homeTeamStats['faceOffWinPercentage'])
        draw.text((19, 36), away_fo, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 35), home_fo, fill=(255,255,255), font=self.font)        
        draw.text((26, 35), f"FO%", fill=(255, 255, 255), font=self.font)

        # PIM
        away_pim = str(awayTeamStats['pim'])
        home_pim = str(homeTeamStats['pim'])
        draw.text((19, 43), away_pim, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 42), home_pim, fill=(255,255,255), font=self.font)
        draw.text((27, 42), f"PIM", fill=(255, 255, 255), font=self.font)

        # Blocks
        away_blk = str(awayTeamStats['blocked'])
        home_blk = str(homeTeamStats['blocked'])
        draw.text((19, 50), away_blk, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 49), home_blk, fill=(255,255,255), font=self.font)        
        draw.text((24, 49), f"bLKS", fill=(255, 255, 255), font=self.font)


        # Getting all goals
        # for i in self.overview.plays['scoringPlays']:
        #     player = self.overview.plays['allPlays'][i]['players'][0]['fullName']
        #     totals = self.overview.plays['allPlays'][i]['players'][0]['seasonTotal']
        #     period = self.overview.plays['allPlays'][i]['about']['ordinalNum']



        # draw.text((26, 56), f"SV%", fill=(255, 255, 255), font=self.font)

        #testing stuff
        # draw.text((18, 35), "SCORERS", fill=(255, 255, 255), font=self.font)
        # draw.text((26, 42), "1st", fill=(255, 255, 255), font=self.font)
        # draw.text((16, 49), "8:47  (PP)", fill=(255, 255, 255), font=self.font)
        # # draw.text((5, 56), "L.Draisaitl (45)", fill=(255, 255, 255), font=self.font)
        # # draw.text((2, 56), "M.Zuccarello (13)", fill=(255, 255, 255), font=self.font)
        # draw.text((1, 56), "Marchessault (99)", fill=(255, 255, 255), font=self.font)
            
        return image
