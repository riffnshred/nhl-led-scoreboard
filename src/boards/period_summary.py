"""
    Shows intermisson stats
"""
from PIL import Image, ImageFont, ImageDraw, ImageOps
from rgbmatrix import graphics
import nhl_api
from data.scoreboard import Scoreboard
from data.team import Team
from data.periods import Periods
from time import sleep
from utils import convert_date_format, get_file
from renderer.logos import LogoRenderer

class PeriodSummary:
    def __init__(self, data, matrix,sleepEvent):
        '''
            TODO:
                Clean up
                only show after game + after periods
                loop thru all favorite teams
        '''
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors
        #Do not forget to change this \/
        self.overview = nhl_api.overview(2022030153) #this is just so I could use any game overview, CHANGE LATER!!!!!!!!!
        #self.data.pref_games[0].game_id
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #self.data.overview
        self.period_instance = Periods(self.overview)
        if self.overview.linescore["currentPeriodTimeRemaining"] == "Final":
            self.display = "Final"
        else:
            self.display = self.period_instance.ordinal
        print(self.display)
        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('team_summary')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        print("OVERVIEW")
        for game in self.data.pref_games:
            print(game.game_id)

        print(self.data.pref_games)
        print(self.overview.home_team_name)
        self.away_color = self.team_colors.color("{}.primary".format(self.overview.away_team_id))
        self.home_color = self.team_colors.color("{}.primary".format(self.overview.home_team_id))
        self.away_text = self.team_colors.color("{}.text".format(self.overview.away_team_id))
        self.home_text = self.team_colors.color("{}.text".format(self.overview.home_team_id))        
        print('PLAYS')
        print(self.overview.plays['scoringPlays'])

    def render(self):
        self.matrix.clear()
        for team_id in self.preferred_teams:
            self.team_id = team_id



            im_height = 65
            for i in enumerate(self.overview.plays['scoringPlays']):
                im_height += 8

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
    def draw_bounding_box(self, position, text, away, home, draw):
        left, top, right, bottom = draw.textbbox((position[0]-1, position[1]-1), text, font=self.font)
        if away > home:
            draw.rectangle((left, top, right, bottom+1), fill=(self.away_color['r'], self.away_color['g'],self.away_color['b']))
            draw.text(position, text, fill=(self.away_text['r'], self.away_text['g'],self.away_text['b']), font=self.font)
        elif home > away:
            draw.rectangle((left, top, right, bottom+1), fill=(self.home_color['r'], self.home_color['g'],self.home_color['b']))
            draw.text(position, text, fill=(self.home_text['r'], self.home_text['g'],self.home_text['b']), font=self.font)
        else:
            draw.text(position, text, fill=(255, 255, 255), font=self.font)
        
    def draw_period_summary(self, im_height):
        image = Image.new('RGB', (64, im_height))
        draw = ImageDraw.Draw(image)
        
        awayTeamStats = self.overview.boxscore['teams']['away']['teamStats']['teamSkaterStats']
        homeTeamStats = self.overview.boxscore['teams']['home']['teamStats']['teamSkaterStats']
        self.draw_bounding_box((1, 1), self.overview.away_team_abrev, 1, 0, draw)
        left, top, right, bottom = draw.textbbox((63, 1), self.overview.home_team_abrev, font=self.font, anchor='rt')
        draw.rectangle((left, top, right, bottom+1), fill=(self.home_color['r'], self.home_color['g'],self.home_color['b']))
        draw.text((64, 2), self.overview.home_team_abrev, fill=(self.home_text['r'], self.home_text['g'],self.home_text['b']), font=self.font, anchor='rt')
        # FINAL = 'Final'
        # ORDINAL = ['Scheduled', '1st', '2nd', '3rd', 'OT', 'SO']
        # ORDINAL_PLAYOFF = ['Scheduled', '1st', '2nd', '3rd', 'OT', '2OT', '3OT', '4OT', '5OT']
        # period_info = overview.linescore
        draw.text((32, 0), self.display, fill=(255,255,255), font=self.font, anchor='mt')
        
        


        # score
        draw.text((27, 8), f"{self.overview.away_score}", fill=(255, 255, 255), font=self.font, anchor='rt')
        draw.text((37, 7), f"{self.overview.home_score}", fill=(255, 255, 255), font=self.font)
        draw.text((30, 7), f"-", fill=(255, 255, 255), font=self.font)

        # SHOTS
        away_sog = awayTeamStats['shots']
        home_sog = homeTeamStats['shots']
        self.draw_bounding_box((26, 14), "SOG", away_sog, home_sog, draw)
        draw.text((19, 15), f"{away_sog}", fill=(255, 255, 255), font=self.font, anchor='rt')
        draw.text((43, 14), f"{home_sog}", fill=(255, 255, 255), font=self.font)


        # PP
        away_pp = f"{int(awayTeamStats['powerPlayGoals'])}/{int(awayTeamStats['powerPlayOpportunities'])}"
        home_pp = f"{int(homeTeamStats['powerPlayGoals'])}/{int(homeTeamStats['powerPlayOpportunities'])}"
        self.draw_bounding_box((28, 21), "PP", awayTeamStats['powerPlayGoals'], homeTeamStats['powerPlayGoals'], draw)
        draw.text((19, 22), away_pp, fill=(255, 255, 255), font=self.font, anchor='rt')  
        draw.text((43, 21), home_pp, fill=(255, 255, 255), font=self.font)

        #HITS
        away_hits = str(awayTeamStats['hits'])
        home_hits = str(homeTeamStats['hits'])
        self.draw_bounding_box((25, 28), "HITS", int(away_hits), int(home_hits), draw)
        draw.text((19, 29), away_hits, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 28), home_hits, fill=(255,255,255), font=self.font)

        # FO%
        away_fo = str(awayTeamStats['faceOffWinPercentage'])
        home_fo = str(homeTeamStats['faceOffWinPercentage'])
        self.draw_bounding_box((26, 35), "FO%", float(away_fo), float(home_fo), draw)
        draw.text((19, 36), away_fo, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 35), home_fo, fill=(255,255,255), font=self.font)

        # PIM
        away_pim = str(awayTeamStats['pim'])
        home_pim = str(homeTeamStats['pim'])
        self.draw_bounding_box((27, 42), "PIM", int(home_pim), int(away_pim), draw)
        draw.text((19, 43), away_pim, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 42), home_pim, fill=(255,255,255), font=self.font)

        # Blocks
        away_blk = str(awayTeamStats['blocked'])
        home_blk = str(homeTeamStats['blocked'])
        self.draw_bounding_box((24, 49), "bLKS", int(away_blk), int(home_blk), draw)
        draw.text((19, 50), away_blk, fill=(255,255,255), font=self.font, anchor = 'rt')
        draw.text((43, 49), home_blk, fill=(255,255,255), font=self.font)        
        
        draw.line([0, 57, 64, 57], fill=(255,255,255))
        
        draw.text((1, 58), "GOALS", fill=(255,255,255), font=self.font)
        # # Getting all goals
        # self.appended_list = []
        # for i in self.overview.plays['scoringPlays']:
        #     id = self.overview.plays['allPlays'][i]['players'][0]['player']['id']
        #     self.appended_list.append(self.overview.players["ID"+str(id)]['lastName'])
        # # Create a dictionary to store the count of each name
        # self.name_count = {}
        # # Iterate through the data
        # self.result = []
        # for name in self.appended_list:
        #     if name in self.name_count:
        #         self.name_count[name] += 1
        #         self.updated_name = f'{name} ({self.name_count[name]})'
        #         self.result.append(self.updated_name)
        #     else:
        #         self.name_count[name] = 1
        #         self.result.append(name)
        # Initialize variables
        appended_list = []
        name_count = {}
        result = []
        goals_scored = 0
        starting_y = 65
        y_step = 7
        y = 0

        # Extract player names and update counts
        for index, scoring_play in enumerate(self.overview.plays['scoringPlays']):
            y = starting_y + goals_scored * y_step
            im_height += 8
            # goals_scored + 1
            # # print(y)
            print(index)
            y = starting_y + (index * 8)
            player_id = self.overview.plays['allPlays'][scoring_play]['players'][0]['player']['id']
            team_id = self.overview.plays['allPlays'][scoring_play]['team']['id']
            player_name = self.overview.players["ID" + str(player_id)]['lastName']
            # print(team_id)
            if team_id == self.overview.away_team_id:
                # print("AWAY")
                away = 1
                home = 0
            else:
                # print("HOME")
                away = 0
                home = 1
            if player_name in name_count:
                name_count[player_name] += 1
                updated_name = f'{player_name} ({name_count[player_name]})'
                result.append(updated_name)
            else:
                name_count[player_name] = 1
                result.append(player_name)
            self.draw_bounding_box((1, y), result[index], away, home, draw)
        # draw.text((1, 65), result[0], fill=(255,255,255), font=self.font)

        print(result)
        return image