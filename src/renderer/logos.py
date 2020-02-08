from PIL import Image
from utils import get_file
from images.image_helper import ImageHelper
import os
import errno

USE_SVGS = True
AUTO_POSITION = True
AUTO_POSITION_OFFSET = 20

PATH = 'assets/logos'
LOGO_NAME = 'teams-current-primary-light'
LOGO_URL = 'https://www-league.nhlstatic.com/images/logos/{}/{}.svg'

class TeamLogos:
    def __init__(self, matrix, layout, team, gameLocation):
        self.matrix = matrix
        self.layout = layout
        self.gameLocation = gameLocation

        self.load(team)

    def get_path(self, team):
        if (USE_SVGS):
            return get_file('{}/{}/{}.png'.format(PATH, team.abbrev, LOGO_NAME))
        
        return get_file('{}/{}.png'.format(PATH, team.abbrev))

    def load(self, team):
        # Get the on-screen position of both logos
        self.location = self.layout.get_scoreboard_logo_coord(
            team.id
        )[self.gameLocation]
        
        filename = self.get_path(team)

        try:
            self.logo = Image.open(filename)
        except FileNotFoundError:
            if (USE_SVGS):
                self.save_image(filename, team)
       
    def save_image(self, filename, team):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                
        self.logo = ImageHelper.image_from_svg(
            LOGO_URL.format(LOGO_NAME, team.id)
        )
        self.logo.thumbnail((64, 32))
        #self.logo = self.logo.transpose(method=Image.FLIP_LEFT_RIGHT)
        self.logo.save(filename)

    def render(self):
        # Put the images on the canvas
        if (AUTO_POSITION):
            x = 0
            
            image_location = "right" if self.gameLocation == "home" else "left"
            if image_location == 'right':
                x = self.logo.width - AUTO_POSITION_OFFSET
            elif image_location == 'left':
                x = AUTO_POSITION_OFFSET - self.logo.width

            self.matrix.draw_image((x, 0), self.logo, image_location)
        else:
            self.matrix.draw_image((self.location["x"], self.location["y"]), self.logo)
