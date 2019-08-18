def scoreboard(team_dict, game_dict):
    for game in game_dict:
        scoreboard = '{0}:{1} - {2}:{3} {4}'.format(team_dict[game['away_team_id']]['abbreviation'], game['away_score'], team_dict[game['home_team_id']]['abbreviation'], game['home_score'], game['game_status'])
        print(scoreboard)

