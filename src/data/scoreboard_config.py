from utils import get_file
from data.layout import Layout
from data.colors import Color
import json
import os
import sys
import debug

class ScoreboardConfig:
    def __init__(self, filename_base, args, width, height):
        json = self.__get_config(filename_base)

        # Misc config options
        self.debug = json["debug"]
        self.live_mode = json["live_mode"]

        # Preferences
        self.end_of_day = json["preferences"]["end_of_day"]
        self.live_game_refresh_rate = json["preferences"]["live_game_refresh_rate"]
        self.preferred_teams = json["preferences"]["teams"]
        self.standing_type = json["preferences"]["standing_type"]
        self.preferred_divisions = json["preferences"]["divisions"]
        self.preferred_conference = json["preferences"]["conference"]

        # Dimmer preferences
        self.dimmer_source = json["preferences"]["dimmer"]["source"]
        self.dimmer_frequency = json["preferences"]["dimmer"]["frequency"]
        self.dimmer_light_level_lux = json["preferences"]["dimmer"]["light_level_lux"]
        self.dimmer_mode = json["preferences"]["dimmer"]["mode"]
        self.dimmer_sunset_brightness = json["preferences"]["dimmer"]["sunset_brightness"]
        self.dimmer_sunrise_brightness = json["preferences"]["dimmer"]["sunrise_brightness"]

        # Boards configuration
        # Boards
        self.boards_off_day = json["boards"]["off_day"]
        self.boards_scheduled = json["boards"]["scheduled"]
        self.boards_intermission = json["boards"]["intermission"]
        self.boards_post_game = json["boards"]["post_game"]

        # Scoreticker
        self.preferred_teams_only = json["boards"]["scoreticker"]["preferred_teams_only"]
        self.scoreticker_rotation_rate = json["boards"]["scoreticker"]["rotation_rate"]

        # Standings
        self.preferred_standings_only = json["boards"]["standings"]["preferred_standings_only"]

        # Element's led coordinates
        self.layout = Layout(self.__get_layout(width, height))

        # load colors
        json = self.__get_colors("teams")
        self.team_colors = Color(json)

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file("config/{}".format(filename))
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)

        reference_config = self.read_json(filename)

        return reference_config

    def __get_colors(self, base_filename):
        try:
            filename = "colors/teams.json".format(base_filename)
            reference_colors = self.read_json(filename)
            return reference_colors
        except:
            debug.error("Invalid {} reference color file. Make sure {} exists in ledcolors/".format(base_filename, base_filename))
            sys.exit(1)

    def __get_layout(self, width, height):
        filename = "renderer/{}x{}_config.json".format(width, height)
        reference_layout = self.read_json(filename)
        if not reference_layout:
            # Unsupported coordinates
            debug.error("Invalid matrix dimensions provided or missing resolution config file (64x32_config.json). This software currently support 64x32 matrix board only.\nIf you would like to see new dimensions supported, please file an issue on GitHub!")
            sys.exit(1)

        return reference_layout
