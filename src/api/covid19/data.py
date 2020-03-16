import requests
import debug as debug

BASE_URL = "https://coronavirus-19-api.herokuapp.com/all"

REQUEST_TIMEOUT = 5
TIMEOUT_TESTING = 0.001  # TO DELETE

def get_all():
    try:
        debug.log("grabbing all data from API")
        data = requests.get(BASE_URL)
        return data.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

class Data:
    def __init__(self):
        self.all = get_all()