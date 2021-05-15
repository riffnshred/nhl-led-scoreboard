import nhl_api.game
import nhl_api.info
import calendar


def day(year, month, day):
    """
        Return a list of games for a certain day.
    """

    # get the days per month
    daysinmonth = calendar.monthrange(year, month)[1]
    # do not even try to get data if day is too high
    if daysinmonth < day:
        return []
    # get data
    data = nhl_api.game.scoreboard(year, month, day)
    return [nhl_api.game.GameScoreboard(data[x]) for x in data]


def teams():
    """Return list of Info objects for each team"""
    return [nhl_api.info.Info(x) for x in nhl_api.info.team_info()]

def player(playerId):
    """Return an Info object of a player information"""
    return nhl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    return nhl_api.game.Overview(nhl_api.game.overview(game_id))


def game_status_info():
    return nhl_api.info.status()


def current_season_info():
    return nhl_api.info.current_season()


def standings():
    # standings, wildcard = nhl_api.info.standings()
    # return nhl_api.info.Standings(standings, wildcard)
    standings = nhl_api.info.standings()
    return nhl_api.info.Standings(standings)


def playoff(season = ""):
    return nhl_api.info.Playoff(nhl_api.info.playoff_info(season))

def series_game_record(seriesCode, season):
    return nhl_api.info.series_record(seriesCode, season)
