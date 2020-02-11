from config.file import ConfigFile, JSONData

class LayoutConfig:
  def __init__(self):
    self.config = ConfigFile('config/layout/dynamic.json')

  def get_scoreboard_logo(self, team, gameLocation):
    logo = self.config.data.scoreboard.logos._default.__copy__()

    logos = self.config.data.scoreboard.logos
    if (team in logos):
      logo.__merge__(logos[team])
      logo.__merge__(logos[team][gameLocation])
      return logo
    
    return logo
