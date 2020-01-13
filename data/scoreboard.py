from data.team import Team
from data.periods import Periods

class Scoreboard:

    def __init__(self, overview):
        linescore = overview.linescore
        away = linescore.teams.away
        home = linescore.teams.home
        self.away_team = Team(away.team.abbreviation, away.team.name, away.goals, away.shotsOnGoal, away.powerPlay,
                              away.numSkaters, away.goaliePulled)
        self.home_team = Team(home.team.abbreviation, home.team.name, home.goals, home.shotsOnGoal, home.powerPlay,
                              home.numSkaters, home.goaliePulled)
        self.status = overview.status
        self.periods = Periods(overview)


    def __str__(self):
        output = "<{} {}> {} (G {}, SOG {}) @ {} (G {}, SOG {}); Status: {}; Period : {} {};".format(
            self.__class__.__name__, hex(id(self)),
            self.away_team.abbrev, str(self.away_team.goals), str(self.away_team.shot_on_goal),
            self.home_team.abbrev, str(self.home_team.goals), str(self.home_team.shot_on_goal),
            self.status,
            self.periods.ordinal,
            self.periods.state
        )
        return output