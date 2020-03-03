from config.file import ConfigFile, JSONData

class LayoutConfig:
  def __init__(self, size):
    self.layout = ConfigFile('config/layout/layout.json', size)
    self.dynamic_layout = ConfigFile('config/layout/layout_{}x{}.json'.format(size[0], size[1]), size)
    self.colors = ConfigFile('config/colors/layout.json')

    # Combine layout for current size with the base layout, overwriting any values found
    self.layout.combine(self.dynamic_layout)

    self.logo_config = ConfigFile('config/layout/logos.json', size)

  def get_board_layout(self, board):
    layouts = self.layout.data
    default_layout = layouts._default.__copy__()

    colors = self.colors.data
    default_color = colors._default

    layout = default_layout
    layout.color = default_color

    if board in layouts:
      layout = layouts[board]

      for element, value in layout:
        if isinstance(value, JSONData):
          layout[element].__merge__(default_layout)
          layout[element].color = default_color

    if board in colors:
      layout_colors = colors[board]

      for element, value in layout_colors:
        layout[element].color = value

    return layout

  def get_scoreboard_logo(self, team, board, gameLocation):
    logo = self.logo_config.data.scoreboard.logos._default.__copy__()

    logos = self.logo_config.data[board].logos
    if (team in logos):
      logo.__merge__(logos[team])
      if (gameLocation != None and gameLocation in logos[team]):
        logo.__merge__(logos[team][gameLocation])
    
    return logo
