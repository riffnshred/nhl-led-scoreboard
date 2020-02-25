import json
from config.files.layout import LayoutConfig

class Config:
  def __init__(self, size):
    self.layout = LayoutConfig(size)