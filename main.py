from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from data.data import Data
from renderer import main
import debug

SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.0"

config = ScoreboardConfig("config")
debug.set_debug_status(config)

data = Data(config)
#todays_date = data.day
todays_games = data.refresh_games()
teams_info = data.get_teams_info()





#print(teams_info[2]['abbreviation'])

print(data.set_date().date())

#main.renderer(data)
print(todays_games)
#display_scoreboards(teams_info, todays_games)

