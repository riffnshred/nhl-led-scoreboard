from PIL import Image
from utils import get_file
from images.image_helper import ImageHelper
import os
import errno
from utils import round_normal

PATH = 'assets/logos'
LOGO_NAME = 'light'
LOGO_URL = 'http://cdn.nhle.com/logos/nhl/svg/{}_{}.svg'

class LogoRenderer:
    def __init__(self, matrix, config, element_layout, team, board, gameLocation=None):
        self.matrix = matrix
        self.layout = config.config.layout.get_scoreboard_logo(
            team.abbrev, 
            board, 
            gameLocation
        )
        
        self.element_layout = element_layout

        self.load(team)

    def get_size(self):
        return (
            int(round_normal(self.matrix.width * self.layout.zoom)), 
            int(round_normal(self.matrix.height * self.layout.zoom))
        )

    def get_path(self, team):
        size = self.get_size()
        return get_file('{}/{}/{}/{}x{}.png'.format(
            PATH, team.abbrev, LOGO_NAME, 
            size[0], size[1]
        ))

    def load(self, team):
        try:
            filename = self.get_path(team)
            self.logo = Image.open(filename)
        except FileNotFoundError:
            self.save_image(filename, team)

        rotate = self.layout.rotate
        flip = self.layout.flip
        crop = self.layout.crop

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
        self.matrix.draw_image_layout(
            self.element_layout, 
            self.logo,
            self.layout.position
        )