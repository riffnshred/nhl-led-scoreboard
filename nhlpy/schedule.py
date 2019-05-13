import requests
import json

from .constants import BASE_URL


class Schedule:
    def today(self, id=None):
        self.id = id
        if self.id == None:
            response = requests.get("{0}/schedule".format(BASE_URL))
            self.data = response.json()
            del self.data["copyright"]
            return self.data
        else:
            response = requests.get("{0}/schedule?teamId={1}".format(BASE_URL, self.id))
            self.data = response.json()
            del self.data["copyright"]
            return self.data

    def date(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

        if self.start_date == None and self.end_date == None:
            return self.today()
        elif self.start_date != None and self.end_date == None:
            response = requests.get(
                "{0}/schedule{1}{2}".format(BASE_URL, "?date=", self.start_date)
            )
            self.data = response.json()
            del self.data["copyright"]
            return self.data
        else:
            return self.today()

    """
    Returns line score for today's completed games. Can't add date parameters to this.
    """

    def linescore(self):
        response = requests.get(
            "{0}/schedule?expand=schedule.linescore".format(BASE_URL)
        )
        self.data = response.json()
        del self.data["copyright"]
        return self.data

    def tickets(self):
        response = requests.get("{0}/schedule?expand=schedule.ticket".format(BASE_URL))
        self.data = response.json()
        del self.data["copyright"]
        return self.data
