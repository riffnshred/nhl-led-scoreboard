import json
import requests
import debug

"""
    TODO:
        Add functions to call single series overview (all the games of a single series) using the NHL record API. 
        https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter="A" and seasonId=20182019
"""

BASE_URL = "http://statsapi.web.nhl.com/api/v1/"
SCHEDULE_URL = BASE_URL + 'schedule?date={0}-{1}-{2}&expand=schedule.linescore'
TEAM_URL = '{0}teams?expand=team.roster,team.stats,team.schedule.previous,team.schedule.next'.format(BASE_URL)
PLAYER_URL = '{0}people/{1}'
PLAYER_STATS_URL = '{0}people/{1}/{2}'
OVERVIEW_URL = BASE_URL + 'game/{0}/feed/live?site=en_nhl'
STATUS_URL = BASE_URL + 'gameStatus'
CURRENT_SEASON_URL = BASE_URL + 'seasons/current'
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


def get_player_stats(playerId):
    try:
        data = requests.get(f"{BASE_URL}people/{playerId}/stats?stats=statsSingleSeason&season=20222023", timeout=REQUEST_TIMEOUT)
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

def get_fav_players_id(config):
    ids = []
    for i in config:
        player = requests.get(f"https://suggest.svc.nhl.com/svc/suggest/v1/minactiveplayers/{i}/100")
        # if the suggestion key has no items move on to the next player
        if not player.json()['suggestions']:
            continue
        ids.append(player.json()["suggestions"][0][0:7]) 
    return ids

def get_point_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()
    
def get_goal_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()

def get_assist_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22assists%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22assists%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()
def get_win_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22wins%22,%22direction%22:%22DESC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22wins%22,%22direction%22:%22DESC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()
def get_plus_minus_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22plusMinus%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22plusMinus%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()

def get_penalty_minute_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22penaltyMinutes%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=[{%22property%22:%22penaltyMinutes%22,%22direction%22:%22DESC%22},{%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()

def get_time_on_ice_leaders(playoffs):
    if playoffs:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/timeonice?isAggregate=false&isGame=false&sort=[{%22property%22:%22timeOnIcePerGame%22,%22direction%22:%22DESC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1%20and%20gamesPlayed%3E=2&cayenneExp=gameTypeId=3%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")
    else:
        data = requests.get("https://api.nhle.com/stats/rest/en/skater/timeonice?isAggregate=false&isGame=false&sort=[{%22property%22:%22timeOnIcePerGame%22,%22direction%22:%22DESC%22},{%22property%22:%22playerId%22,%22direction%22:%22ASC%22}]&start=0&limit=4&factCayenneExp=gamesPlayed%3E=1%20and%20gamesPlayed%3E=2&cayenneExp=gameTypeId=2%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023")

    return data.json()
