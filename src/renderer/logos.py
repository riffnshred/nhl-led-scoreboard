from PIL import Image
from utils import get_file
from images.image_helper import ImageHelper
import os
import errno

USE_SVGS = True
AUTO_POSITION = True
AUTO_POSITION_OFFSET = 21

PATH = 'assets/logos'
LOGO_NAME = 'light'
LOGO_URL = 'http://cdn.nhle.com/logos/nhl/svg/{}_{}.svg'

class TeamLogos:
    def __init__(self, matrix, config, team, gameLocation):
        self.matrix = matrix
        self.layout = config.layout

        self.new_layout = config.config.layout.get_scoreboard_logo(team.abbrev, gameLocation)
        self.gameLocation = gameLocation

        self.load(team)

    def get_size(self):
        return (
            int(round(self.matrix.width * self.new_layout.zoom)), 
            int(round(self.matrix.height * self.new_layout.zoom))
        )

    def get_path(self, team):
        if (USE_SVGS):
            size = self.get_size()
            return get_file('{}/{}/{}/{}x{}.png'.format(
                PATH, team.abbrev, LOGO_NAME, 
                size[0], size[1]
            ))
        
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

        if (USE_SVGS):
          rotate = self.new_layout.rotate
          flip = self.new_layout.flip
          crop = self.new_layout.crop

          if (rotate != 0):
              self.logo = self.logo.rotate(rotate, expand=True)
          if (flip == 1):
              self.logo = self.logo.transpose(method=Image.FLIP_LEFT_RIGHT)
          if (crop != 0):
              self.logo = self.logo.crop((
                  self.logo.width * (crop[0]),
                  self.logo.height * (crop[1]),
                  self.logo.width - (self.logo.width * (crop[2])),
                  self.logo.height - (self.logo.height * (crop[3])),
              ))
       
    def save_image(self, filename, team):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                
        self.logo = ImageHelper.image_from_svg(
            LOGO_URL.format(team.abbrev, LOGO_NAME)
        )

        self.logo.thumbnail(self.get_size())
        self.logo.save(filename)

    def render(self):
        # Put the images on the canvas
        if (AUTO_POSITION):
            offset = self.new_layout.offset
            x = 0
            
            image_location = "right" if self.gameLocation == "home" else "left"
            if image_location == 'right':
                x = self.logo.width - AUTO_POSITION_OFFSET
            elif image_location == 'left':
                x = AUTO_POSITION_OFFSET - self.logo.width

            x += (self.logo.width * offset[0])
            y = -((self.logo.height - self.matrix.height) / 2) + (self.logo.height * offset[1])

            self.matrix.draw_image((x, y), 
                self.logo, 
                image_location
            )
        else:
            self.matrix.draw_image((self.location["x"], self.location["y"]), self.logo)
