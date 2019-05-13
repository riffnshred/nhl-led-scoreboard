import requests
import json

from .constants import BASE_URL


class Game:
    def __init__(self, id):
        self.id = id

    def all_stats(self):
        response = requests.get("{0}/game/{1}/feed/live".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def boxscore(self):
        response = requests.get("{0}/game/{1}/boxscore".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def media(self):
        response = requests.get("{0}/game/{1}/content".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]
        return self.data
