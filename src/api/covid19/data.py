import requests
import debug as debug

BASE_URL = "https://corona.lmao.ninja/"
WW_URL = BASE_URL + 'all'
COUNTRY_URL = BASE_URL + 'countries'
US_STATE_URL = BASE_URL + 'states'
CANADA_URL = BASE_URL + 'v2/jhucsse'

REQUEST_TIMEOUT = 5
TIMEOUT_TESTING = 0.001  # TO DELETE


class Data:
    def __init__(self):
        pass
    
    def get_all(self):
        debug.log("Grabbing all COVID-19 data from API")
        try:
            data = requests.get(WW_URL)
            data.raise_for_status()
            self.ww = data.json()
        except requests.exceptions.RequestException as e:
            #raise ValueError(e)
            print(e)
        try:
            data = requests.get(COUNTRY_URL)
            data.raise_for_status()
            self.country_data = data.json()
            self.countrydict = {}
            for country in self.country_data:
                self.countrydict[country["country"]] = country 
        except requests.exceptions.RequestException as e:
            #raise ValueError(e)
            print(e)
        try:    
            data = requests.get(US_STATE_URL)
            data.raise_for_status()
            self.us_state = data.json()
            self.us_state_dict = {}
            for state in self.us_state:
                self.us_state_dict[state["state"]] = state
        except requests.exceptions.RequestException as e:
            print(e)
            #raise ValueError(e)
        try:    
            data = requests.get(CANADA_URL)
            data.raise_for_status()
            self.canada_prov = data.json()
            self.canada_prov_dict = {}
            for prov in self.canada_prov:
                self.canada_prov_dict[prov["province"]] = prov            
        except requests.exceptions.RequestException as e:
            print(e)
            #raise ValueError(e)
