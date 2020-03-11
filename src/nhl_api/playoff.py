import nhl_api.data
import nhl_api.object
import debug

def playoff_info():
    data = nhl_api.data.get_playoff_data()
    parsed = data.json()
    playoff_data = parsed["rounds"]

    default_round = parsed["defaultRound"]
    rounds = []

    for round in playoff_data:
        number = round['number']
        name = round['names']['name']


class PlayoffRound(object):
    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                obj = nhl_api.object.Object(data[x])
                setattr(self, x, obj)
