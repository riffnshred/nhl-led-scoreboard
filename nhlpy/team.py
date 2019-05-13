import requests
import json

from .constants import BASE_URL


class Team:
    def __init__(self, id):
        self.id = id

    def info(self):
        response = requests.get("{0}/teams/{1}".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def roster(self):
        path = "?expand=team.roster"
        response = requests.get("{0}/teams/{1}{2}".format(BASE_URL, self.id, path))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def next_game(self):
        path = "?expand=team.schedule.next"
        response = requests.get("{0}/teams/{1}{2}".format(BASE_URL, self.id, path))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def last_game(self):
        path = "?expand=team.schedule.previous"
        response = requests.get("{0}/teams/{1}{2}".format(BASE_URL, self.id, path))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    """
    Returns single season stats, regular season stat rankings, and general information about team
    """

    def stats(self):
        path = "?expand=team.stats"
        response = requests.get("{0}/teams/{1}{2}".format(BASE_URL, self.id, path))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    """
    Only returns the single season stats and regular season stat ranknings
    """

    def simple_stats(self):
        path = "stats"
        response = requests.get("{0}/teams/{1}/{2}".format(BASE_URL, self.id, path))
        self.data = response.json()
        del self.data["copyright"]
        return self.data
