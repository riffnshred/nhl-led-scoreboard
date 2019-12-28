import requests
import datetime
from utils import convert_time

NHL_API_URL = "http://statsapi.web.nhl.com/api/v1/"
NHL_API_URL_BASE = "http://statsapi.web.nhl.com"


# TEST_URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2018-01-02&endDate=2018-01-02"

def get_teams():
    """
        Function to get a list of all the teams information
        The info for each team are store in multidimensional dictionary like so:
        {
            team ID{
                team name,
                fullname,
                location,
                abbreviation,
                conference name,
                division name
            }
        }
        This make it a lot simpler to call each info of a specific team as all info in the API are associated with a team ID
    """

    url = '{0}/teams'.format(NHL_API_URL)
    response = requests.get(url)
    results = response.json()
    teams_info = {}
    try:
        for team in results['teams']:
            info_dict = {'name': team['teamName'], 'fullname': team['name'],
                         'location': team['locationName'],
                         'abbreviation': team['abbreviation'], 'conference': team['conference']['name'],
                         'division': team['division']['name']}
            teams_info[team['id']] = info_dict

        return teams_info
    except requests.exceptions.RequestException:
        print("Error encountered getting teams info, Can't reach the NHL API")

def fetch_overview(game_id):
    """
    Function to get the score of the game live depending on the chosen team.
    Inputs the game ID and returns the score found on web.
    """

    # Set URL depending on team selected
    url = '{0}game/2019020448/feed/live?site=en_nhl'.format(NHL_API_URL)

    try:
        game_data = requests.get(url)
        game_data = game_data.json()

        # General game data
        game_status = game_data['gameData']['status']['detailedState']
        game_time = convert_time(game_data["gameData"]['datetime']['dateTime']).strftime("%I:%M")
        period = game_data['liveData']['linescore']['currentPeriodOrdinal']
        time = game_data['liveData']['linescore']['currentPeriodTimeRemaining']

        # Powerplay
        powerplay_strength = game_data['liveData']['linescore']['powerPlayStrength']


        # Teams related Data
        home_team_id = int(game_data['gameData']['teams']['home']['id'])
        home_score = int(game_data['liveData']['linescore']['teams']['home']['goals'])
        home_SOG = int(game_data['liveData']['linescore']['teams']['home']['shotsOnGoal'])
        home_goalie_pulled = game_data['liveData']['linescore']['teams']['home']['goaliePulled']
        home_powerplay = game_data['liveData']['linescore']['teams']['home']['powerPlay']
        away_team_id = int(game_data['liveData']['linescore']['teams']['away']['goals'])
        away_score = int(game_data['liveData']['linescore']['teams']['away']['goals'])
        away_SOG = int(game_data['liveData']['linescore']['teams']['away']['shotsOnGoal'])
        away_goalie_pulled = game_data['liveData']['linescore']['teams']['away']['goaliePulled']
        away_powerplay = game_data['liveData']['linescore']['teams']['away']['powerPlay']

        # Putting the data together to send back.
        game_overview = {'game_status': game_status, 'game_time': game_time, 'period': period, 'time': time,
                         'home_team_id': home_team_id, 'powerplay_strength': powerplay_strength,
                         'home_score': home_score, 'home_SOG': home_SOG, 'home_goalie_pulled': home_goalie_pulled,
                         'home_powerplay': home_powerplay, 'away_team_id': away_team_id, 'away_score': away_score,
                         'away_SOG': away_SOG, 'away_goalie_pulled': away_goalie_pulled,
                         'away_powerplay': away_powerplay}

        return game_overview
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except KeyError:
        print("missing data from the game. Game has not begun or is not scheduled today.")


def fetch_fav_team_schedule(team_id):
    """ Function to get the summary of a scheduled game. """
    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)

    try:
        game_data = requests.get(url)
        game_data = game_data.json()

        home_team_id = int(game_data['dates'][0]['games'][0]['teams']['home']['team']['id'])
        away_team_id = int(game_data['dates'][0]['games'][0]['teams']['away']['team']['id'])

        game_time = convert_time(game_data["dates"][0]["games"][0]["gameDate"]).strftime("%I:%M")

        current_game_schedule = {'home_team_id': home_team_id, 'away_team_id': away_team_id, 'game_time': game_time}

        return current_game_schedule
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except KeyError:
        print("missing data from the game. Game has not begun or is not scheduled today.")


def check_season():
    """ Function to check if in season. Returns True if in season, False in off season. """
    # Get current time
    now = datetime.datetime.now()
    if now.month in (7, 8):
        return False
    else:
        return True

#
# NOT USING IT FOR THE MOMENT BUT MIGHT BE USEFUL LATER FOR OTHER FEATURES
#####
def fetch_games(teams_id=False):
    """
    Function to get a dictionary of today's games.

    request stats in json form from the schedule section of the NHL API URL
    loop through the games received and organize each data with a key in a dictionary:

    finally return a dictionary containing each games info organized by their Game Id:

    ex: gameid: {
                    'full_stats_link'
                    'home_team_id'
                    'home_score'
                    'away_team_id'
                    'away_score'
                    'game_status'
                    'game_time'
                }

    game_dict = dictionary of all the games.
    url = the API link where we can find the list of games.
    """
    if teams_id:
        # Set URL depending with team selected
        url = '{0}schedule?teamId={1}'.format(NHL_API_URL, ','.join(map(str, teams_id)))
    else:
        url = '{0}schedule'.format(NHL_API_URL)

    game_dict = {}
    try:
        game_data = requests.get(url)
        game_data = game_data.json()
        games = game_data['dates'][0]['games']
        for game in range(len(games)):
            live_stats_link = game_data['dates'][0]['games'][game]['link']
            game_id = int(game_data['dates'][0]['games'][game]['gamePk'])
            home_team_id = int(game_data['dates'][0]['games'][game]['teams']['home']['team']['id'])
            home_score = int(game_data['dates'][0]['games'][game]['teams']['home']['score'])
            away_team_id = int(game_data['dates'][0]['games'][game]['teams']['away']['team']['id'])
            away_score = int(game_data['dates'][0]['games'][game]['teams']['away']['score'])
            game_status = int(game_data['dates'][0]['games'][0]['status']['statusCode'])
            game_time = convert_time(game_data["dates"][0]["games"][game]["gameDate"]).strftime("%I:%M")

            game_dict[game_id] = {"full_stats_link": live_stats_link, "home_team_id": home_team_id,
                        "home_score": home_score, "away_team_id": away_team_id, "away_score": away_score,
                        'game_status': game_status, 'game_time': game_time}

        return game_dict
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except IndexError:
        print("No Game today")
        return game_list