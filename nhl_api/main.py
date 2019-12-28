import nhl_api.data as data
import nhl_api.game
import nhl_api.info

def test_game():
    games = nhl_api.game.scoreboard(2019, 12, 17)
    games_list = [nhl_api.game.GameScoreboard(games[x]) for x in games]
    for game in games_list:
        print(game)

def test_team_info():
    team_list = [x['team_id'] for x in nhl_api.info.team_info()]
    print(team_list)

def test_overview():
    game_info = nhl_api.game.overview('2017020659')
    game_info = nhl_api.game.Overview(game_info)
    print(game_info.gameData.status.detailedState)

def test_status_info():
    data = nhl_api.info.status()
    for status in data:
        print(status)

# Test Games
#test_game()

# Test Info
#test_team_info()

# Test overview
#test_overview()

# Test status
test_status_info()
