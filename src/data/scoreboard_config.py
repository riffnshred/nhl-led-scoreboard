from utils import get_file
from data.layout import Layout
from data.colors import Color
from config.main import Config  
import json
import os
import sys
import debug

class ScoreboardConfig:
    def __init__(self, filename_base, args, size):
        json = self.__get_config(filename_base)

        # Misc config options
        self.debug = json["debug"]
        self.live_mode = json["live_mode"]

        # Preferences
        self.end_of_day = json["preferences"]["end_of_day"]
        self.time_format = self.__get_time_format(json["preferences"]["time_format"])
        self.live_game_refresh_rate = json["preferences"]["live_game_refresh_rate"]
        self.preferred_teams = json["preferences"]["teams"]

        # Goal animation
        self.goal_anim_pref_team_only = json["goal_animations"]["pref_team_only"]

        # Dimmer preferences
        self.dimmer_enabled = json["dimmer"]["enabled"]
        self.dimmer_source = json["dimmer"]["source"]
        self.dimmer_frequency = json["dimmer"]["frequency"]
        self.dimmer_light_level_lux = json["dimmer"]["light_level_lux"]
        self.dimmer_mode = json["dimmer"]["mode"]
        self.dimmer_sunset_brightness = json["dimmer"]["sunset_brightness"]
        self.dimmer_sunrise_brightness = json["dimmer"]["sunrise_brightness"]

        # States
        '''TODO: Put condition so that the user dont leave any board list empty'''
        self.boards_off_day = json["states"]["off_day"]
        self.boards_scheduled = json["states"]["scheduled"]
        self.boards_intermission = json["states"]["intermission"]
        self.boards_post_game = json["states"]["post_game"]

        # Boards configuration
        # Boards
        # Scoreticker
        self.preferred_teams_only = json["boards"]["scoreticker"]["preferred_teams_only"]
        self.scoreticker_rotation_rate = json["boards"]["scoreticker"]["rotation_rate"]

        # Standings
        self.preferred_standings_only = json["boards"]["standings"]["preferred_standings_only"]
        self.standing_type = json["boards"]["standings"]["standing_type"]
        self.preferred_divisions = json["boards"]["standings"]["divisions"]
        self.preferred_conference = json["boards"]["standings"]["conference"]

        # Clock
        self.clock_board_duration = json["boards"]["clock"]["duration"]
        self.clock_hide_indicators = json["boards"]["clock"]["hide_indicator"]

        # Element's led coordinates
        self.layout = Layout(self.__get_config(
            "layout/{}x{}_config".format(size[0], size[1]),
            "Invalid matrix dimensions provided or missing resolution config file (64x32_config.json). This software currently support 64x32 matrix board only.\nIf you would like to see new dimensions supported, please file an issue on GitHub!"
        ))

        # load colors 
        self.team_colors = Color(self.__get_config(
            "colors/teams"
        ))

        self.config = Config(size)

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file("config/{}".format(filename))
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename, error=None):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)

        reference_config = self.read_json(filename)
        if not reference_config:
            if (error):
                debug.error(error)
            else:
                debug.error("Invalid {} config file. Make sure {} exists in config/".format(base_filename, base_filename))
            sys.exit(1)

        return reference_config

    def __get_time_format(self, config):
        # Set the time format to 12h.
        time_format = "%I:%M"

        # Check if the time format is different in the config. if so, change it.
        if config == "24h":
            time_format = "%H:%M"

        return time_format
