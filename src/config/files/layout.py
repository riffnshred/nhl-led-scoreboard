from config.file import ConfigFile, JSONData

class LayoutConfig:
  def __init__(self, size, fonts):
    self.layout = ConfigFile('config/layout/layout.json', size)
    self.dynamic_layout = ConfigFile('config/layout/layout_{}x{}.json'.format(size[0], size[1]), size, False)
    # Combine layout for current size with the base layout, overwriting any values found
    self.layout.combine(self.dynamic_layout)

    self.logo_config = ConfigFile('config/layout/logos.json', size)
    self.dynamic_logo_config = ConfigFile('config/layout/logos_{}x{}.json'.format(size[0], size[1]), size, False)
    self.logo_config.combine(self.dynamic_logo_config)

    self.colors = ConfigFile('config/colors/layout.json')
    self.fonts = fonts

  def get_board_layout(self, board):
    layouts = self.layout.data
    default_layout = layouts._default.__copy__()

    colors = self.colors.data
    default_color = colors._default

    layout = default_layout
    layout.color = default_color

    if board in layouts:
      layout = layouts[board].__copy__()

      for element, value in layout:
        layout[element].font = self.fonts.get_font(value.font if hasattr(value, 'font') else None)

        if isinstance(value, JSONData):
          layout[element].__merge__(default_layout)
          layout[element].color = default_color

    if board in colors:
      layout_colors = colors[board]

      for element, value in layout_colors:
        layout[element].color = value

    return layout

  def get_scoreboard_logo(self, team, board, gameLocation, variant):
    logo = self.logo_config.data.scoreboard.logos._default.__copy__()

    logos = self.logo_config.data[board].logos

    conf_set = logos["_default"]
    if (team in logos):
      conf_set = logos[team]
      if (variant in logos[team]):
        conf_set = logos[team][variant]
      
    logo.__merge__(conf_set, overwrite=True)
        
    if (gameLocation != None and gameLocation in conf_set):
        logo.__merge__(conf_set[gameLocation], overwrite=True)
    
    return logo
