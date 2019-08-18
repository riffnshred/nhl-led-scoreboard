from renderer.scoreboard_renderer import scoreboard
import time
import sys

print('NHL Scoreboard V0.01')
print('Gathering nhl data')

def debug(team_data):
    game_data = [{'gameid': 2017020608, 'full_stats_link': '/api/v1/game/2017020608/feed/live', 'home_team_id': 30, 'home_score': 5, 'away_team_id': 13, 'away_score': 1, 'game_status': 'Final'}]
    scoreboard(team_data,game_data)

def renderer(data):
    try:
        print("Press CTRL-C to stop.")
        c = 0
        while True:
            debug(data.get_teams_info)
            time.sleep(10)
            c += 1
            print(c)

    except KeyboardInterrupt:
        sys.exit(0)
