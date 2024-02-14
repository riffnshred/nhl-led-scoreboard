import nhl_api.game
import nhl_api.info
import datetime

from nhlpy import NHLClient


def player(playerId):
    """Return an Info object of a player information"""
    return nhl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    return nhl_api.game.overview(game_id)

def play_by_play(game_id):
    client = Client(base_url="https://api-web.nhle.com")
    game_details = {}
    #with client as client:
    game_details = get_game_play_by_play_by_id.sync(game_id, client=client)
    return game_details

def game_status_info():
    return nhl_api.info.status()


def current_season_info():
    return nhl_api.info.current_season()

def next_season_info():
    return nhl_api.info.next_season()

def standings():
    # TODO: Wildcard stuff
    season_standings = {}

    client = NHLClient(verbose=False)
    #with client as client:
    season_standings = client.standings.get_standings(date = str(datetime.date.today()))

    return nhl_api.info.Standings(season_standings, {})


def playoff(season = ""):
    return nhl_api.info.Playoff(nhl_api.info.playoff_info(season))

def series_game_record(seriesCode, season):
    return nhl_api.info.series_record(seriesCode, season)
