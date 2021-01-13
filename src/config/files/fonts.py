from config.file import ConfigFile
from PIL import ImageFont
from utils import get_file

class FontsConfig:
  def __init__(self, size):
    self.config = ConfigFile('config/fonts/fonts.json')
    self.dynamic_config = ConfigFile('config/fonts/fonts_{}x{}.json'.format(size[0], size[1]), size, False)

    self.config.combine(self.dynamic_config)

    self.load_fonts()

  def load_fonts(self):
    self.fonts = {}

    for element, value in self.config.data:
      self.fonts[element] = ImageFont.truetype(
        get_file("assets/fonts/{}".format(value['file'])), 
        value['size']
      )

  def get_font(self, id=None):
    if id in self.fonts:
      return self.fonts[id]
    
    return self.fonts['_default']