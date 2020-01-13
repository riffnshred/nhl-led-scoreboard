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

        # Preferences
        self.preferred_teams = json["preferences"]["teams"]
        self.preferred_divisions = json["preferences"]["divisions"]
        self.standing_type = json["preferences"]["standing_type"]

        # Rotation
        self.preferred_teams_only = json["rotation"]["preferred_teams_only"]


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
