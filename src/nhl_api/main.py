import nhl_api.game
import nhl_api.info

def test_game():
    games = nhl_api.game.scoreboard(2019, 12, 17)
    games_list = [nhl_api.game.GameScoreboard(games[x]) for x in games]
    for game in games_list:
        print(game)

def test_team_info():
    team_list = [x['team_id'] for x in nhl_api.info.team_info()]
    team_info = [nhl_api.info.Info(x) for x in nhl_api.info.team_info()]
    info_by_id = {}
    for team in team_info:
        info_by_id[team.team_id] = team

    print(info_by_id[8].abbreviation)

def test_overview():
    game_info = nhl_api.game.overview('2017020659')
    game_info = nhl_api.game.Overview(game_info)
    print(game_info.linescore.intermissionInfo.inIntermission)

def test_status_info():
    data = nhl_api.info.status()
    for status in data:
        print(status)

def test_standings():
    global wc
    standings, wildcard = nhl_api.info.standings()
    standings = nhl_api.info.Standings(standings, wildcard)
    standings = standings.by_conference

    # for record in standings.eastern.wild_card:
    #     print(record)

    # for team in standings.central:
    #     pos = team['divisionRank']
    #     team_name = team['team_name']
    #     points = team['points']
    #     wins = team['leagueRecord']['wins']
    #     losses = team['leagueRecord']['losses']
    #     ot = team['leagueRecord']['ot']
    #     message = "{}. {} - Points: {} - W: {} L: {} OT: {}".format(pos, team_name, points, wins, losses, ot)
    #     print(message)

    for conf, value in vars(standings).items():
        print(conf)
        for type, value in vars(value).items():
            if type == "wild_card":
                wc = value
            else:
                for div, value in vars(value).items():
                    print(div)
                    for record in value:
                        show_div_record(record)
                if wc:
                    print("wildcard")
                    for record in wc:
                        show_wild_card_record(record)

    # print('EASTERN')
    # for team in standings.eastern:
    #
    #     pos = team['conferenceRank']
    #     team_name = team['team_name']
    #     points = team['points']
    #     wins = team['leagueRecord']['wins']
    #     losses = team['leagueRecord']['losses']
    #     ot = team['leagueRecord']['ot']
    #
    #     message = "{}. {} - Points: {} - W: {} L: {} OT: {}".format(pos, team_name, points,  wins, losses, ot)
    #     print(message)
    #
    # print("\r")
    # print('WESTERN')
    #
    # for team in standings.western:
    #     pos = team['conferenceRank']
    #     team_name = team['team_name']
    #     points = team['points']
    #     wins = team['leagueRecord']['wins']
    #     losses = team['leagueRecord']['losses']
    #     ot = team['leagueRecord']['ot']
    #
    #     message = "{}. {} - Points: {} - W: {} L: {} OT: {}".format(pos, team_name, points,  wins, losses, ot)
    #     print(message)

def show_wild_card_record(record):
    pos = record['wildCardRank']
    team_name = record["team"]['name']
    points = record['points']
    wins = record['leagueRecord']['wins']
    losses = record['leagueRecord']['losses']
    ot = record['leagueRecord']['ot']
    message = "{}. {} - Points: {} - W: {} L: {} OT: {}".format(pos, team_name, points, wins, losses, ot)
    print(message)


def show_div_record(record):
    pos = record['divisionRank']
    team_name = record["team"]['name']
    points = record['points']
    wins = record['leagueRecord']['wins']
    losses = record['leagueRecord']['losses']
    ot = record['leagueRecord']['ot']
    message = "{}. {} - Points: {} - W: {} L: {} OT: {}".format(pos, team_name, points, wins, losses, ot)
    print(message)

# Test Games
#test_game()

# Test Info
#test_team_info()

# Test overview
#test_overview()

# Test status
#test_status_info()

# Test standings
test_standings()
