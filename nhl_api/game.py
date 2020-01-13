"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from nhl_api.utils import convert_time
import nhl_api.data
import nhl_api.object


def scoreboard(year, month, day):
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = nhl_api.data.get_schedule(year, month, day)
    if not data:
        return data
    parsed = data.json()

    if parsed["dates"]:
        games_data = parsed["dates"][0]["games"]
        games = {}
        for game in games_data:
            game_id = game['gamePk']
            season = game['season']
            game_type = game['gameType']
            game_date = game['gameDate']

            home_team_id = int(game['teams']['home']['team']['id'])
            home_team_name = game['teams']['home']['team']['name']
            away_team_id = int(game['teams']['away']['team']['id'])
            away_team_name = game['teams']['away']['team']['name']
            home_score = game['teams']['home']['score']
            away_score = game['teams']['away']['score']

            status = game['status']['detailedState']
            status_code = game['status']['statusCode']
            status_abstract_state = game['status']['abstractGameState']

            if game['linescore'] and game['linescore']['currentPeriod'] > 0:
                current_period = game['linescore']['currentPeriod']
                current_period_ordinal = game['linescore']['currentPeriodOrdinal']
                current_period_time_remaining = game['linescore']['currentPeriodTimeRemaining']
            else:
                current_period = game['linescore']['currentPeriod']
                current_period_ordinal = False
                current_period_time_remaining = False

            output = {
                'game_id': game_id,
                'season': season,
                'game_type': game_type,
                'game_date': game_date,
                'home_team_id': home_team_id,
                'home_team_name': home_team_name,
                'away_team_id': away_team_id,
                'away_team_name': away_team_name,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                'status_code': status_code,
                'status_abstract_state': status_abstract_state,
                'current_period': current_period,
                'current_period_ordinal': current_period_ordinal,
                'current_period_time_remaining': current_period_time_remaining
            }

            # put this dictionary into the larger dictionary
            games[game_id] = output
        return games
    else:
        return []


class GameScoreboard(object):

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

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d %I:%M")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})').format(self)


def overview(game_id):
    data = nhl_api.data.get_overview(game_id)
    parsed = data.json()

    # Top level information (General)
    id = parsed['gamePk']
    time_stamp = parsed['gameData']['game']
    game_type = parsed['gameData']['game']['type']
    status = parsed['gameData']['status']['detailedState']
    game_date = parsed['gameData']['datetime']['dateTime']

    # Sub level information (Details)
    away_team = parsed['gameData']['teams']['away']
    home_team = parsed['gameData']['teams']['home']
    plays = parsed['liveData']['plays']
    linescore = parsed['liveData']['linescore']

    output = {
        'id': id,  # ID of the game
        'time_stamp': time_stamp,  # Last time the data was refreshed (UTC)
        'game_type': game_type,  # Type of game ("R" for Regular season, "P" for Post season or playoff)
        'status': status,   # Status of the game.
        'game_date': game_date,  # Date and time of the game
        'away_team': away_team,  # Information about the Away team (ID, Name, Abbreviation, Division and Conference, etc)
        'home_team': home_team,  # Information about the Home team (ID, Name, Abbreviation, Division and Conference, etc)
        'plays': plays,  # Dictionary of all the plays of the game.
        'linescore': linescore  # Dictionary of all the line score related data (Periods, Goals, SOG etc...)
    }
    return output


class Overview(object):
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

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d %I:%M")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")
