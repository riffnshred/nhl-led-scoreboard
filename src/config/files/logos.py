from config.file import ConfigFile
import os.path

class LogosConfig:
  def __init__(self):
    if os.path.isfile('config/custom_logos.json'):
      self.config = ConfigFile('config/custom_logos.json')
    else:
      self.config = ConfigFile('config/logos.json')

  def get_team_logo(self, team):
    logos = self.config.data

    if (team in logos):
      return logos[team]

    return logos["_default"]