import requests
import debug as debug

BASE_URL = "https://corona.lmao.ninja/"
WW_URL = BASE_URL + 'all'
COUNTRY_URL = BASE_URL + 'countries'
US_STATE_URL = BASE_URL + 'states'

REQUEST_TIMEOUT = 5
TIMEOUT_TESTING = 0.001  # TO DELETE


class Data:
    def __init__(self):
        pass
    
    def get_all(self):
        try:
            debug.log("grabbing all data from API")
            data = requests.get(WW_URL)
            self.ww = data.json()
            data = requests.get(COUNTRY_URL)
            self.country_data = data.json()
            self.countrydict = {}
            for country in self.country_data:
                 self.countrydict[country["country"]] = country 
            data = requests.get(US_STATE_URL)
            self.us_state = data.json()
            self.us_state_dict = {}
            for state in self.us_state:
                 self.us_state_dict[state["state"]] = state
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
