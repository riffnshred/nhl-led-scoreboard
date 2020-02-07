from PIL import ImageFont
from utils import get_file

class Layout:
    """
        TODO: Need to work on the layout class to make it expendable and easy to add new layout
    """
    def __init__(self, coordinates):
        self.coord = coordinates

        # Load the fonts
        self.font_large = ImageFont.truetype(get_file("assets/fonts/score_large.otf"), 16)
        self.font = ImageFont.truetype(get_file("assets/fonts/04B_24__.TTF"), 8)
        self.font_large_2 = ImageFont.truetype(get_file("assets/fonts/A-15-BIT.ttf"), 12)

    def get_scoreboard_logo_coord(self, team_id):
        return self.coord["scoreboard"]["logos"][str(team_id)]

    def _get_summary_logo_coord(self, team_id):
        return self.coord["team_summary"]["logos"][str(team_id)]

    def _get_standings_coods(self):
        return self.coord["standings"]