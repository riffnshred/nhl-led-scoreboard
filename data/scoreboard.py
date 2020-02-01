from data.team import Team
from data.periods import Periods

class Scoreboard:
    def __init__(self, overview, teams_info):

        linescore = overview.linescore
        away = linescore.teams.away
        home = linescore.teams.home
        away_abbrev = teams_info[away.team.id].abbreviation
        home_abbrev = teams_info[home.team.id].abbreviation
        self.away_team = Team(away.team.id, away_abbrev, away.team.name, away.goals, away.shotsOnGoal, away.powerPlay,
                              away.numSkaters, away.goaliePulled)
        self.home_team = Team(home.team.id, home_abbrev, home.team.name, home.goals, home.shotsOnGoal, home.powerPlay,
                              home.numSkaters, home.goaliePulled)
        self.date = overview.full_date
        self.start_time = overview.start_time
        self.status = overview.status
        self.periods = Periods(overview)

        if self.status == "Final":
            self.winning_team = overview.w_team
            self.loosing_team = overview.l_team

    def __str__(self):
        output = "<{} {}> {} (G {}, SOG {}) @ {} (G {}, SOG {}); Status: {}; Period : {} {};".format(
            self.__class__.__name__, hex(id(self)),
            self.away_team.name, str(self.away_team.goals), str(self.away_team.shot_on_goal),
            self.home_team.name, str(self.home_team.goals), str(self.home_team.shot_on_goal),
            self.status,
            self.periods.ordinal,
            self.periods.clock
        )
        return output