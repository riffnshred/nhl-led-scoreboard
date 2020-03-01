from config.file import ConfigFile, JSONData

class LayoutConfig:
  def __init__(self, size):
    self.config = ConfigFile('config/layout/layout.json', size)
    self.logo_config = ConfigFile('config/layout/logos.json', size)

  def get_board_layout(self, board):
    layouts = self.config.data
    layout = self.config.data._default.__copy__()

    if (board in layouts):

      layout = layouts[board].__copy__()

    return layout

  def get_scoreboard_logo(self, team, board, gameLocation):
    logo = self.logo_config.data.scoreboard.logos._default.__copy__()

    logos = self.logo_config.data[board].logos
    if (team in logos):
      logo.__merge__(logos[team])
      if (gameLocation != None and gameLocation in logos[team]):
        logo.__merge__(logos[team][gameLocation])
    
    return logo
