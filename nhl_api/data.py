import requests
import debug

BASE_URL = "http://statsapi.web.nhl.com/api/v1/"
SCHEDULE_URL = BASE_URL + 'schedule?date={0}-{1}-{2}'
TEAM_URL = '{0}/teams'.format(BASE_URL)
OVERVIEW_URL = BASE_URL + 'game/{0}/feed/live?site=en_nhl'
STATUS_URL = BASE_URL + 'gameStatus'
CURRENT_SEASON_URL = BASE_URL + 'seasons/current'
MODIFIER_TEAM_ID = "?teamId={}"


def get_schedule(year, month, day):
    try:
        data = requests.get(SCHEDULE_URL.format(year, month, day))
    except requests.exceptions.RequestException:
        debug.error("Failed to retrieve schedule")

    return data


def get_teams():
    try:
        data = requests.get(TEAM_URL)
    except requests.exceptions.RequestException:
        debug.error("Failed to retrieve schedule")

    return data


def get_overview(game_id):
    try:
        data = requests.get(OVERVIEW_URL.format(game_id))
    except requests.exceptions.RequestException:
        debug.error("Failed to retrieve the Overview")

    return data


def get_game_status():
    try:
        data = requests.get(STATUS_URL)
    except requests.exceptions.RequestException:
        debug.error("Failed to retrieve the list of status")

    return data

def get_current_season():
    try:
        data = requests.get(CURRENT_SEASON_URL)
    except requests.exceptions.RequestException:
        debug.error("Failed to retrieve the list of status")

    return data