from data.team import SeriesTeam
from utils import convert_time

class Series:
    def __init__(self, series, data):

        """
            Get all games of a series through this.
            https://records.nhl.com/site/api/playoff-series?cayenneExp=playoffSeriesLetter="A" and seasonId=20182019

            This is off from the nhl record api. Not sure if it will update as soon as the day is over. 
        """
        
        matchupTeams = series.matchupTeams
        top, bottom = self.get_team_position(self.matchupTeams)
        top_team_abbrev = data.teams_info[top.team.id].abbreviation
        bottom_team_abbrev = data.teams_info[bottom.team.id].abbreviation
        self.matchup_short_name = series.names.matchupShortName
        self.top_team = SeriesTeam(top, top_team_abbrev)
        self.bottom_team = SeriesTeam(bottom, bottom_team_abbrev)
        self.bottom_team_abbrev = series.names.teamAbbreviationB
        self.current_game = series.currentGame.seriesSummary
        self.current_game_id = series.currentGame.seriesSummary.gamePk
        self.short_status = series.currentGame.seriesSummary.seriesStatusShort

        self.current_game_date = convert_time(overview.game_date).strftime("%Y-%m-%d")
        self.current_game_start_time = convert_time(overview.game_date).strftime(time_format)

        def get_team_position(teams_info):
            """
                Lookup for both team's position in the seed data of team's info and return 
                their data in respective position (top_team, bottom_team)
            """
            while i <= 1:
                bottom_team = teams_info[i]
                if bottom_team.seed.isTop:
                    top_team = bottom_team
            
            return top_team, bottom_team