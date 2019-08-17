import requests
import datetime

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
            info_dict = {'name': team['teamName'], 'location': team['locationName'], 'abbreviation': team['abbreviation'], 'conference': team['conference']['name'], 'division': team['division']['name']}
            teams[team['id']] = info_dict
        return teams
    except requests.exceptions.RequestException:
        print("Error encountered getting teams info")

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
        print("Error encountered getting live stats")


def fetch_games(date = None):
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
    if date is not None:
        url = '{0}schedule?date={1}'.format(NHL_API_URL, date)
    else:
        url = '{0}schedule'.format(NHL_API_URL)

    game_list = []
    try:
        score = requests.get(url)
        score = score.json()
        games = score['dates'][0]['games']
        for game in range(len(games)):
            live_stats_link = score['dates'][0]['games'][game]['link']
            game_id = int(score['dates'][0]['games'][game]['gamePk'])
            home_team_id = int(score['dates'][0]['games'][game]['teams']['home']['team']['id'])
            home_score = int(score['dates'][0]['games'][game]['teams']['home']['score'])
            away_team_id = int(score['dates'][0]['games'][game]['teams']['away']['team']['id'])
            away_score = int(score['dates'][0]['games'][game]['teams']['away']['score'])
            game_status = score['dates'][0]['games'][game]['status']['abstractGameState']

            gameInfo = {"gameid":game_id, "full_stats_link":live_stats_link, "home_team_id":home_team_id, "home_score":home_score, "away_team_id":away_team_id, "away_score":away_score, 'game_status':game_status}

            game_list.append(gameInfo)
        return game_list
    except requests.exceptions.RequestException:
        print("Error encountered, returning 0 for score")
    except IndexError:
        print("No Game today")
        return game_list


def fetch_score(team_id):
    """ Function to get the score of the game depending on the chosen team.
    Inputs the team ID and returns the score found on web. """

    # Get current time
    now = datetime.datetime.now()

    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    # Avoid request errors (might still not catch errors)
    try:
        score = requests.get(url)
        score = score.json()
        if int(team_id) == int(score['dates'][0]['games'][0]['teams']['home']['team']['id']):
            score = int(score['dates'][0]['games'][0]['teams']['home']['score'])
        else:
            score = int(score['dates'][0]['games'][0]['teams']['away']['score'])

        # Print score for test
        # print("Score: {0} Time: {1}:{2}:{3}".format(score, now.hour, now.minute, now.second))
        return score
    except requests.exceptions.RequestException:
        print("Error encountered, returning 0 for score")
        return 0


def check_season():
    """ Function to check if in season. Returns True if in season, False in off season. """
    # Get current time
    now = datetime.datetime.now()
    if now.month in (7, 8):
        return False
    else:
        return True


def check_if_game(team_id,date):
    """ Function to check if there is a game now with chosen team. Returns True if game, False if NO game. """
    # Set URL depending on team selected
    if date is not None:
        url = '{0}schedule?teamId={1}&startDate={2}&endDate={2}'.format(NHL_API_URL,team_id,Date)
    else:
        url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)

    try:
        gameday_url = requests.get(url)
        if "gamePk" in gameday_url.text:

            live_stats_link = score['dates'][0]['games'][game]['link']
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, returning True for check_game")
        return True


def check_game_end(team_id):
    """ Function to check if the game ofchosen team is over. Returns True if game, False if NO game. """

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
