import nhl_api.game
import nhl_api.info
from nhl_api_client import Client
from nhl_api_client.api.game import get_game_play_by_play_by_id
from nhl_api_client.api.default import get_season_standings_by_date
from nhl_api_client.models import SeasonStandings
import datetime

def player(playerId):
    """Return an Info object of a player information"""
    return nhl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    return nhl_api.game.overview(game_id)

def play_by_play(game_id):
    client = Client(base_url="https://api-web.nhle.com")
    game_details = {}
    with client as client:
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

    client = Client(base_url="https://api-web.nhle.com")
    with client as client:
        season_standings: SeasonStandings = get_season_standings_by_date.sync(str(datetime.date.today()), client=client)

    return nhl_api.info.Standings(season_standings, {})


def playoff(season = ""):
    return nhl_api.info.Playoff(nhl_api.info.playoff_info(season))

def series_game_record(seriesCode, season):
    return nhl_api.info.series_record(seriesCode, season)
