import json
import requests
import debug
import dotty_dict
import logging

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
DIFF_OVERVIEW_URL = BASE_URL + \
    'game/{0}/feed/live/diffPatch?site=en_nhl&startTimecode={1}'
STATUS_URL = BASE_URL + 'gameStatus'
CURRENT_SEASON_URL = BASE_URL + 'seasons/current'
STANDINGS_URL = BASE_URL + 'standings'
STANDINGS_WILD_CARD = STANDINGS_URL + '/wildCardWithLeaders'
PLAYOFF_URL = BASE_URL + "tournaments/playoffs?expand=round.series,schedule.game.seriesSummary&season={}"
SERIES_RECORD = "https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter='{}' and seasonId={}"
REQUEST_TIMEOUT = 5

TIMEOUT_TESTING = 0.001  # TO DELETE

logger = logging.getLogger('scoreboard')
scoreboards = {}


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
    if game_id in scoreboards:
        try:
          return get_diff_overview(game_id)
        except ValueError:
        #    return full overview if diff fails
           return get_full_overview(game_id)


    return get_full_overview(game_id)


def get_full_overview(game_id):
    try:
        data = requests.get(OVERVIEW_URL.format(game_id), timeout=REQUEST_TIMEOUT).json()
        scoreboards[game_id] = data
        # data = dummie_overview()
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def get_diff_overview(game_id):
    try:
        data = scoreboards[game_id]
        startTimecode = data['metaData']['timeStamp']
        diffs = requests.get(DIFF_OVERVIEW_URL.format(
            game_id, startTimecode), timeout=REQUEST_TIMEOUT).json()
        # data = dummie_overview()
        data = apply_patches(data, diffs)
        scoreboards[game_id] = data
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


def apply_patches(data, diffs):
    dot = dotty_dict.Dotty(data, separator='/')
    for patches in diffs:
        logger.debug(patches)
        for patch in patches['diff']:
            path = patch['path'].strip('/')
            if patch['op'] in ['replace', 'add']:
                dot[path] = patch['value']
            elif patch['op'] in ['remove']:
                if dot.get(path):
                    del dot[path]
            else:
                return get_full_overview(data['gamePk'])
    return dot.to_dict()


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
