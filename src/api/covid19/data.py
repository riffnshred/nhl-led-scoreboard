import requests
import debug as debug

BASE_URL = "https://corona.lmao.ninja/countries/us"

REQUEST_TIMEOUT = 5
TIMEOUT_TESTING = 0.001  # TO DELETE


class Data:
    def __init__(self):
        pass
    
    def get_all(self):
        try:
            debug.log("grabbing all data from API")
            data = requests.get(BASE_URL)
            self.all = data.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(e)

