from config.file import ConfigFile

class LogosConfig:
  def __init__(self):
    self.config = ConfigFile('config/logos.json')

  def get_team_logo(self, team):
    logos = self.config.data

    if (team in logos):
      return logos[team]

    return logos["_default"]