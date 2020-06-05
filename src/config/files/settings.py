from config.file import ConfigFile

class SettingsConfig:
  def __init__(self):
    self.config = ConfigFile('config/config.json')

  