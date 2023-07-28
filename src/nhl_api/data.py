import json
import requests
import debug
from datetime import date

"""
    TODO:
        Add functions to call single series overview (all the games of a single series) using the NHL record API. 
        https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter="A" and seasonId=20182019
"""

BASE_URL = "http://statsapi.web.nhl.com/api/v1/"
SCHEDULE_URL = BASE_URL + 'schedule?date={0}-{1}-{2}&expand=schedule.linescore'
TEAM_URL = '{0}teams?expand=team.roster,team.stats,team.schedule.previous,team.schedule.next'.format(BASE_URL)
PLAYER_URL = '{0}people/{1}'
OVERVIEW_URL = BASE_URL + 'game/{0}/feed/live?site=en_nhl'
STATUS_URL = BASE_URL + 'gameStatus'
CURRENT_SEASON_URL = BASE_URL + 'seasons/current'
NEXT_SEASON_URL = BASE_URL + 'seasons/{0}'
STANDINGS_URL = BASE_URL + 'standings'
STANDINGS_WILD_CARD = STANDINGS_URL + '/wildCardWithLeaders'
PLAYOFF_URL = BASE_URL + "tournaments/playoffs?expand=round.series,schedule.game.seriesSummary&season={}"
SERIES_RECORD = "https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter='{}' and seasonId={}"
REQUEST_TIMEOUT = 5

TIMEOUT_TESTING = 0.001  # TO DELETE


def get_schedule(year, month, day):
    try:
        data = requests.get(SCHEDULE_URL.format(year, month, day), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_teams():
    try:
        data = requests.get(TEAM_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_player(playerId):
    try:
        data = requests.get(PLAYER_URL.format(BASE_URL, playerId), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_overview(game_id):
    try:
        data = requests.get(OVERVIEW_URL.format(game_id), timeout=REQUEST_TIMEOUT)
        # data = dummie_overview()
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_game_status():
    try:
        data = requests.get(STATUS_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_current_season():
    try:
        data = requests.get(CURRENT_SEASON_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)
    
def get_next_season():
    # Create the next seasonID from the current year and curent year +1 eg: 20232024 is seasonID for 2023-2024 season
    # This will return an empty set for seasons data if the seasonID has nothing, a 200 response will always occur
    current_year = date.today().year
    next_year = current_year + 1
    
    nextseasonID="{0}{1}".format(current_year,next_year)
    
    try:
        data = requests.get(NEXT_SEASON_URL.format(nextseasonID), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_standings():
    try:
        data = requests.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_standings_wildcard():
    try:
        data = requests.get(STANDINGS_WILD_CARD, timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_playoff_data(season):
    try:
        data = requests.get(PLAYOFF_URL.format(season), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

def get_series_record(seriesCode, season):
    try:
        data = requests.get(SERIES_RECORD.format(seriesCode, season), timeout=REQUEST_TIMEOUT)
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)

## DEBUGGING DATA (TO DELETE)
def dummie_overview():
    with open('dummie_nhl_data/overview_reg_final.json') as json_file:
        data = json.load(json_file)
        return data
