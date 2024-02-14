"""
    Shows list of series summary (Table with each result of game).
"""
from time import sleep
from utils import center_obj
from data.playoffs import Series
from data.scoreboard import Scoreboard
from renderer.matrix import MatrixPixels
import debug
import nhlpy

class Seriesticker:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.rotation_rate = 5
        self.matrix = matrix
        self.spacing = 3 # Number of pixel between each dot + 1
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        self.font = data.config.layout.font
        self.layout = self.data.config.config.layout.get_board_layout('scoreticker')
        self.team_colors = self.data.config.team_colors

    def render(self):
        if not self.data.current_round:
            debug.log("No Playoff to render on seriesticker")
            return
        self.allseries = self.data.series
        self.index = 0
        self.num_series = len(self.allseries)

        for series in self.allseries:
            self.matrix.clear()
            banner_text = "Stanley Cup"
            color_banner_bg = (200,200,200)
            color_banner_text = (0,0,0)
            round_name = "Final" 

            if not self.data.current_round.number == 4:
                try:
                    color_conf = self.team_colors.color("{}.primary".format(series.conference))
                    banner_text = series.conference
                except:
                    color_conf = self.team_colors.color("{}.primary".format("Western"))
                    banner_text = "Western"
                color_banner_bg = (color_conf['r'], color_conf['g'], color_conf['b'])
                round_name = self.data.current_round_name
                self.show_indicator(self.index, self.num_series)
            
            self.matrix.draw_text(
                (1, 7),
                round_name,
                font=self.font,
                fill=(255,255,255)
            )
            # Conference banner, Round Title
            self.matrix.draw.rectangle([0,0,self.matrix.width,5], fill=color_banner_bg)
            self.matrix.draw_text(
                (1, 1), 
                banner_text, 
                font=self.font, 
                fill=(0,0,0)
            )
            self.index += 1
            
            # # If something fails in the process of drawing the series table due to failed API request
            # # Continue in the loop and skip this series.
            # if not self.draw_series_table(series):
            #     debug.error('Failed Draw the series table due to failed API request. Skiping to the next series')
            #     continue


            self.draw_series_table(series)
            self.matrix.render()
            self.sleepEvent.wait(self.data.config.seriesticker_rotation_rate)

    def draw_series_table(self, series):

        color_top_bg = self.team_colors.color("{}.primary".format(series.top_team.id))
        color_top_team = self.team_colors.color("{}.text".format(series.top_team.id))

        color_bottom_bg = self.team_colors.color("{}.primary".format(series.bottom_team.id))
        color_bottom_team = self.team_colors.color("{}.text".format(series.bottom_team.id))

        # Table
        self.matrix.draw.line([(0,21),(self.matrix.width,21)], width=1, fill=(150,150,150))

        # use rectangle because I want to keep symmetry for the background of team's abbrev
        self.matrix.draw.rectangle([0,14,12,20], fill=(color_top_bg['r'], color_top_bg['g'], color_top_bg['b']))
        self.matrix.draw_text(
            (1, 15), 
            series.top_team.abbrev, 
            font=self.font, 
            fill=(color_top_team['r'], color_top_team['g'], color_top_team['b'])
        )

        self.matrix.draw.rectangle([0,22,12,28], fill=(color_bottom_bg['r'], color_bottom_bg['g'], color_bottom_bg['b']))
        self.matrix.draw_text(
            (1, 23), 
            series.bottom_team.abbrev, 
            font=self.font, 
            fill=(color_bottom_team['r'], color_bottom_team['g'], color_bottom_team['b'])
        )
        
        rec_width = 0
        top_row = 15
        bottom_row = 23
        loosing_color = (150,150,150)

        # text offset for loosing score if the winning team has a score of 10 or higher and loosing team 
        # have a score lower then 10

        offset_correction = 0
        for game in series.games:
            attempts_remaining = 5
            while attempts_remaining > 0:
                try:
                    if game["gameId"] in series.game_overviews:
                        # Look if the game data is already stored in the game overviews from the series
                        overview = series.game_overviews[game["gameId"]]
                    else:
                        # Request and store the game overview in the series instance
                        overview = series.get_game_overview(game["gameId"])
                    
                    # get the scoreboard
                    try:
                        scoreboard = Scoreboard(overview, self.data)
                    except:
                        break
                    if self.data.status.is_final(overview.status) and hasattr(scoreboard, "winning_team"):
                        if scoreboard.winning_team == series.top_team.id:
                            winning_row = top_row
                            loosing_row = bottom_row
                            winning_team_color = color_top_team
                            winning_bg_color = color_top_bg
                        else:
                            winning_row = bottom_row
                            loosing_row = top_row
                            winning_team_color = color_bottom_team
                            winning_bg_color = color_bottom_bg

                        # Look loosing score text needs an offset
                        if len(str(scoreboard.winning_score)) == 2 and len(str(scoreboard.winning_score)) == 1:
                            offset_correction = 1
                        
                        self.matrix.draw_text(
                            ((rec_width + 15 + offset_correction), loosing_row), 
                            str(scoreboard.loosing_score), 
                            font=self.font, 
                            fill=loosing_color,
                            backgroundColor=None, 
                            backgroundOffset=[1, 1, 1, 1]
                        )

                        position = self.matrix.draw_text(
                            (rec_width + 15, winning_row), 
                            str(scoreboard.winning_score), 
                            font=self.font, 
                            fill=(winning_team_color['r'], winning_team_color['g'], winning_team_color['b']), 
                            backgroundColor=(winning_bg_color['r'], winning_bg_color['g'], winning_bg_color['b']), 
                            backgroundOffset=[1, 1, 1, 1]
                        )

                        # Increment 
                        rec_width += (position["size"][0] + 4)
                    break

                except ValueError as error_message:
                    self.data.network_issues = True
                    debug.error("Failed to get the Games for the {} VS {} series: {} attempts remaining".format(series.top_team.abbrev, series.bottom_team.abbrev, attempts_remaining))
                    debug.error(error_message)
                    attempts_remaining -= 1
                    self.sleepEvent.wait(1)
                except KeyError as error_message:
                    debug.error("Failed to get the overview for game id {}. Data unavailable or is TBD".format(game["gameId"]))
                    debug.error(error_message)
                    break
            # If one of the request for player info failed after 5 attempts, return an empty dictionary
            if attempts_remaining == 0:
                return False


    def show_indicator(self, index, slides):
        """
            TODO: This function need to be coded a better way. but it works :D

            Carousel indicator.
        """
        align = 0
        spacing = 3

        # if there is more then 11 games, reduce the spacing of each dots
        if slides > 10:
            spacing = 2

            # Move back the indicator by 1 pixel if the number of games is even.
            if slides % 2:
              align = -1

        pixels = []

        # Render the indicator
        for i in range(slides):
            dot_position = ((spacing * i) - 1) + 1

            color = (70, 70, 70)
            if i == index:
                color = (255, 50, 50)

            pixels.append(
              MatrixPixels(
                ((align + dot_position), 0), 
                color
              )
            )

        self.matrix.draw_pixels_layout(
            self.layout.indicator_dots,
            pixels,
            (pixels[-1].position[0] - pixels[0].position[0], 1)
        )
