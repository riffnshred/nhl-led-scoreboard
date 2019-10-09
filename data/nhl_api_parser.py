import requests
import datetime
import time
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
    teams = {}
    try:
        for team in results['teams']:
            info_dict = {'name': team['teamName'], 'location': team['locationName'],
                         'abbreviation': team['abbreviation'], 'conference': team['conference']['name'],
                         'division': team['division']['name']}
            teams[team['id']] = info_dict
        return teams
    except requests.exceptions.RequestException:
        print("Error encountered getting teams info, Can't reach the NHL API")


def fetch_live_stats(link):
    """ Function to get the live stats of the current game """
    url = '{0}{1}'.format(NHL_API_URL_BASE, link)
    response = requests.get(url)
    stuff = response.json()
    try:
        current_period = int(stuff['liveData']['linescore']['currentPeriod'])
        home_sog = int(stuff['liveData']['linescore']['teams']['home']['shotsOnGoal'])
        away_sog = int(stuff['liveData']['linescore']['teams']['away']['shotsOnGoal'])
        home_powerplay = int(stuff['liveData']['linescore']['teams']['home']['powerPlay'])
        away_powerplay = int(stuff['liveData']['linescore']['teams']['away']['powerPlay'])
        try:
            time_remaining = stuff['liveData']['linescore']['currentPeriodTimeRemaining']
        except KeyError:
            time_remaining = "00:00"
        return current_period, home_sog, away_sog, home_powerplay, away_powerplay, time_remaining
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")


def fetch_games():
    """
    Function to get a list of games

    request stats in json form from the schedule section of the NHL API URL
    create a list to store all the games
    loop through the games received and store the info in the created list:
        - for each games:
            - the ID of the game
            - the link to the complete stats of that game
            - the Home team
            - the Home team score
            - the Away team
            - the Away team score
            - game status

    finally return the list of games

    now = the current date from datetime
    game_list = list of all the games and the number of games.
    url = the location where we can find the list of games.
    """

    url = '{0}schedule'.format(NHL_API_URL)

    game_list = []
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
            game_status = game_data['dates'][0]['games'][game]['status']['abstractGameState']
            game_time = convert_time(game_data["dates"][0]["games"][game]["gameDate"]).strftime("%H:%M")

            gameInfo = {"gameid": game_id, "full_stats_link": live_stats_link, "home_team_id": home_team_id,
                        "home_score": home_score, "away_team_id": away_team_id, "away_score": away_score,
                        'game_status': game_status, 'game_time': game_time}

            game_list.append(gameInfo)
        return game_list
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
    except IndexError:
        print("No Game today")
        return game_list


def fetch_overview(team_id):
    """ Function to get the score of the game depending on the chosen team.
    Inputs the team ID and returns the score found on web. """
    print(team_id)
    # Get current time
    now = datetime.datetime.now()

    # Set URL depending on team selected
    url = '{0}schedule?expand=schedule.linescore&teamId={1}'.format(NHL_API_URL, team_id)

    try:
        game_data = requests.get(url)
        game_data = game_data.json()

        period = game_data['dates'][0]['games'][0]['linescore']['currentPeriodOrdinal']
        time = game_data['dates'][0]['games'][0]['linescore']['currentPeriodTimeRemaining']
        home_team_id = int(game_data['dates'][0]['games'][0]['teams']['home']['team']['id'])
        home_score = int(game_data['dates'][0]['games'][0]['teams']['home']['score'])
        away_team_id = int(game_data['dates'][0]['games'][0]['teams']['away']['team']['id'])
        away_score = int(game_data['dates'][0]['games'][0]['teams']['away']['score'])
        game_status = game_data['dates'][0]['games'][0]['status']['abstractGameState']
        game_time = convert_time(game_data["dates"][0]["games"][0]["gameDate"]).strftime("%H:%M")

        current_game_overview = {'period': period, 'time': time, 'home_team_id': home_team_id, 'home_score': home_score,
                                 'away_team_id': away_team_id, 'away_score': away_score, 'game_status': game_status,
                                 'game_time': game_time}

        print(current_game_overview)
        return current_game_overview
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


def check_if_game(team_id):
    """ Function to check if there is a game now with chosen team. Returns True if game, False if NO game. """
    # Set URL depending with team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    print("Check if game")
    try:
        game_data = requests.get(url)
        game_data = game_data.json()
        game = game_data["totalGames"]
        if game != 0:
            status = game_data["dates"][0]["games"][0]['status']['abstractGameState']
            return status
        else:
            return False
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, Can't reach the NHL API")
        return False


def check_game_end(team_id):
    """ Function to check if the game of chosen team is over. Returns True if game, False if NO game. """

    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    # Avoid request errors
    try:
        game_status = requests.get(url)
        game_status = game_status.json()
        game_status = int(game_status['dates'][0]['games'][0]['status']['statusCode'])
        if game_status == 7:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # Return False to allow for another pass for test
        print("Error encountered, returning False for check_game_end")
        return False