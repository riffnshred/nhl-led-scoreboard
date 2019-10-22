from utils import get_file
import json
import os


class ScoreboardConfig:
    def __init__(self, filename_base, args):
        json = self.__get_config(filename_base)

        # Misc config options
        self.end_of_day = json["end_of_day"]
        self.demo_date = json["demo_date"]
        self.debug = json["debug"]

        # config options from arguments. If the argument was passed, use it's value, else use the one from config file.
        self.fav_team_id = args.fav_team if True else json['fav_team_id']

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
