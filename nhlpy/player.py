import requests
import json

from .constants import BASE_URL


class Player:
    def __init__(self, id):
        self.id = id

    """
    Gets details for player, id must be specified to return data
    """

    def info(self):
        response = requests.get("{0}/people/{1}".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    """
    Get single season stats for a player. Two valid consecutive years must
    be specified.
    """

    def season(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=statsSingleSeason&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def home_away(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=homeAndAway&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def win_loss(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=winLoss&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_month(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=byMonth&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_day(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=byDayOfWeek&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_division(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=vsDivision&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_conference(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=vsConference&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_team(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=vsTeam&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def split_by_game(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=gameLog&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def standing(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=regularSeasonStatRankings&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def goals_by_situation(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=goalsByGameSituation&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    """
    This only works with the current in-progress season during the regular season
    """

    def on_pace_stats(self, year_start, year_end):
        self.year_start = year_start
        self.year_end = year_end
        path = "stats?stats=onPaceRegularSeason&season="
        response = requests.get(
            "{0}/people/{1}/{2}{3}{4}".format(
                BASE_URL, self.id, path, self.year_start, self.year_end
            )
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data
