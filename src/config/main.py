import json
from config.files.layout import LayoutConfig
from config.files.settings import SettingsConfig
from config.files.fonts import FontsConfig

class Config:
  def __init__(self, size):
    self.settings = SettingsConfig()
    self.fonts = FontsConfig(size)
    self.layout = LayoutConfig(size, self.fonts)