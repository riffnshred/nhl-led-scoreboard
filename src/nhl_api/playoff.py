import nhl_api.data
import nhl_api.object
import debug

def playoff_info():
    data = nhl_api.data.get_playoff_data()
    parsed = data.json()
    playoff_data = parsed["rounds"]
    rounds = []

    for round in playoff_data:
        pass