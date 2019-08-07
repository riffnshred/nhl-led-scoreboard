from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from data.data import Data
import debug

SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.0"

config = ScoreboardConfig("config")
debug.set_debug_status(config)

data = Data(config)
#todays_date = data.day
todays_games = data.refresh_games()
teams_info = data.get_teams_info()

def display_scoreboards(team_dict, game_dict):

    for game in game_dict:
        scoreboard = '{0}:{1} - {2}:{3} {4}'.format(team_dict[game['away_team_id']]['abbreviation'], game['away_score'], team_dict[game['home_team_id']]['abbreviation'], game['home_score'], game['game_status'])
        print(scoreboard)

print(teams_info[2]['abbreviation'])
print(todays_games)
display_scoreboards(teams_info, todays_games)

