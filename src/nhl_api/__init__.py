import nhl_api.game
import nhl_api.info
import calendar

def player(playerId):
    """Return an Info object of a player information"""
    return nhl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    return nhl_api.game.overview(game_id)


def game_status_info():
    return nhl_api.info.status()


def current_season_info():
    return nhl_api.info.current_season()

def next_season_info():
    return nhl_api.info.next_season()

def standings():
    try:
        standings, wildcard = nhl_api.info.standings()
        return nhl_api.info.Standings(standings, wildcard)
    except:
        return False


def playoff(season = ""):
    return nhl_api.info.Playoff(nhl_api.info.playoff_info(season))

def series_game_record(seriesCode, season):
    return nhl_api.info.series_record(seriesCode, season)
