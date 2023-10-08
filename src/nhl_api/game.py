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

    if parsed["games"]:
        games_data = parsed["games"]
        games = {}
        for game in games_data:
            game_id = game['id']
            season = game['season']
            game_type = game['gameType']
            game_date = game['startTimeUTC']

            home_team_id = int(game['homeTeam']['id'])
            home_team_name = game['homeTeam']['name']
            away_team_id = int(game['awayTeam']['id'])
            away_team_name = game['awayTeam']['name']
            
            try:
                home_score = game['homeTeam']['score']
                away_score = game['awayTeam']['score']
            except:
                home_score = 0
                away_score = 0

            status = game['gameState']
            # status_code = game['status']['statusCode'] # Depricated in new API (2023)
            status_abstract_state = game['gameState']
            # linescore = game['linescore'] # I think this is not used anywhere. Linescore is requested in the Overview side of things

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
                # 'status_code': status_code,
                'status_abstract_state': status_abstract_state,
                # All the linescore information (goals, sog, periods etc...)
                # 'linescore': linescore, # Not used 
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
            except TypeError:
                obj = nhl_api.object.Object(data[x])
                setattr(self, x, obj)

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})\n' ).format(self)

    def __repr__(self):
        return self.__str__()


def overview(game_id):
    data = nhl_api.data.get_overview(game_id)
    parsed = data.json()
    # Top level information (General)
    id = parsed['id']
    
    # time_stamp = parsed['gameData']['game'] # Not used and depricated
    game_type = parsed['gameType']
    status = parsed['gameState']
    # status_code = parsed['gameData']['status']['statusCode'] # Not used and depricated
    # status_abstract_state = parsed['gameData']['status']['abstractGameState'] # Not used and depricated
    game_date = parsed['startTimeUTC']

    # Team details
    away_team_id = parsed['awayTeam']['id']
    away_team_name = parsed['awayTeam']['name']
    away_team_abrev = parsed['awayTeam']['abbrev']
    home_team_id = parsed['homeTeam']['id']
    home_team_name = parsed['homeTeam']['name']
    home_team_abrev = parsed['homeTeam']['abbrev']
    
    try:
        # Sub level information (Details)
        linescore = parsed['summary']['linescore'] # Completly different on the new API
        clock = parsed['clock'] # use to be part of the linescore, but is now appart
        #boxscore = parsed['liveData']['boxscore']
        away_score = linescore['totals']['away']
        home_score = linescore['totals']['home']
    except:
        linescore = {}
        clock = "00:00"
        away_score = 0
        home_score = 0
        
    # 3 stars (if any available)
    try:
        first_star = parsed['threeStars'][0]
        second_star = parsed['threeStars'][1]
        third_star = parsed['threeStars'][2]

    except:
        first_star = {}
        second_star = {}
        third_star = {}

    output = {
        'id': id,  # ID of the game
        # 'time_stamp': time_stamp,  # Last time the data was refreshed (UTC) #Not used and Depricated
        # Type of game ("R" for Regular season, "P" for Post season or playoff)
        'game_type': game_type,
        'status': status,   # Status of the game.
        
        #'status_code': status_code,
        #'status_abstract_state': status_abstract_state,
        'game_date': game_date,  # Date and time of the game
        'away_team_id': away_team_id,  # ID of the Away team
        'away_team_name': away_team_name,  # Away team name
        'away_team_abrev': away_team_abrev,  # Away team name abbreviation
        'home_team_id': home_team_id,  # ID of the Home team
        'home_team_name': home_team_name,  # Home team name
        'home_team_abrev': home_team_abrev,  # Home team name abbreviation
        'away_score': away_score,  # Away team goals
        'home_score': home_score,  # Home team goals
        'linescore': linescore,
        'clock': clock,
        'first_star': first_star,
        'second_star': second_star,
        'third_star': third_star
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
                if isinstance(data[x], list):
                    list_data = data[x]
                    obj_list = []
                    for index in range(len(list_data)):
                        obj_list.append(nhl_api.object.Object(list_data[index]))
                    setattr(self, x, obj_list)
                else:
                    obj = nhl_api.object.Object(data[x])
                    setattr(self, x, obj)
        
        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.w_score = self.home_score
            self.l_team = self.away_team_id
            self.l_score = self.away_score
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.w_score = self.away_score
            self.l_team = self.home_team_id
            self.l_score = self.home_score
            
    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS {0.home_team_name} ({0.home_score})\n'
                'Status: {0.status}\n'
                'Clock: {0.clock.timeRemaining}\n'
                '------------------------\n'
                ).format(self)

    def __repr__(self):
        return self.__str__()