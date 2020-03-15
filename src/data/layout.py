from PIL import ImageFont
from utils import get_file

class Layout:
    def __init__(self):
        # Load the fonts
        self.font_large = ImageFont.truetype(get_file("assets/fonts/score_large.otf"), 16)
        self.font_pb = ImageFont.truetype(get_file("assets/fonts/score_large.otf"), 22)
        self.font = ImageFont.truetype(get_file("assets/fonts/04B_24__.TTF"), 8)
        self.font_large_2 = ImageFont.truetype(get_file("assets/fonts/04B_24__.TTF"), 24)
