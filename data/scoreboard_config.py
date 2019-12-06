from utils import get_file
import json
import os


class ScoreboardConfig:
    #def __init__(self, filename_base, args):
    def __init__(self, filename_base):
        json = self.__get_config(filename_base)

        # Misc config options
        self.end_of_day = json["end_of_day"]
        self.debug = json["debug"]
        self.rotate_preferred_teams_only = json["rotate_preferred_teams_only"]

        # Preferences
        self.preferred_teams = json["preferences"]["teams"]
        self.preferred_divisions = json["preferences"]["divisions"]

        # config options from arguments. If the argument was passed, use it's value, else use the one from config file.
        # if args.fav_team:
        #     self.pref_team_id = args.fav_team
        # else:
        #     self.pref_team_id = json['pref_team_id']

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file(filename)
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)
        reference_config = self.read_json(filename)

        return reference_config
