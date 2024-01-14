from data.team import SeriesTeam
from data.scoreboard import Scoreboard
from utils import convert_time
import nhlpy
import debug

def get_team_position(teams_info):
    """
        Lookup for both team's position in the seed data of team's info and return 
        their data in respective position (top_team, bottom_team)
    """
    for team in teams_info:
        bottom_team = team
        if bottom_team.seed.isTop:
            top_team = bottom_team
    
    return top_team, bottom_team

class Playoff:
    def __init__(self, playoff, data):
        pass

class Rounds(Playoff):
    def __init__(self, round, data):
        pass

class Series:
    def __init__(self, series, data):

        """
            Get all games of a series through this.
            https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter="A" and seasonId=20182019

            This is off from the nhl record api. Not sure if it will update as soon as the day is over. 
        """
        
        matchupTeams = series.matchupTeams
        top, bottom = get_team_position(matchupTeams)
        top_team_abbrev = data.teams_info[top.team.id].abbreviation
        bottom_team_abbrev = data.teams_info[bottom.team.id].abbreviation
        try:
            self.conference = series.conference.name
        except:
            self.conference = ""
        self.series_number = series.seriesNumber
        self.series_code = series.seriesCode #To use with the nhl records API
        
        self.matchup_short_name = series.names.matchupShortName
        self.top_team = SeriesTeam(top, top_team_abbrev)
        self.bottom_team = SeriesTeam(bottom, bottom_team_abbrev)
        self.current_game = series.currentGame.seriesSummary
        self.current_game_id = series.currentGame.seriesSummary.gamePk
        self.short_status = series.currentGame.seriesSummary.seriesStatusShort

        self.current_game_date = convert_time(self.current_game.gameTime).strftime("%Y-%m-%d")
        self.current_game_start_time = convert_time(self.current_game.gameTime).strftime(data.config.time_format)
        self.games = nhlpy.series_game_record(self.series_code, data.playoffs.season)
        self.game_overviews = {}

    def get_game_overview(self, gameid):
        # Request the game overview
        overview = ""
        try:
            overview = nhlpy.play_by_play
        except:
            debug.error("failed overview refresh for series game id {}".format(gameid))
        self.game_overviews[gameid] = overview
        return overview
        



        

        
