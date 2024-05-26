class Team:
    def __init__(self, id, abbrev, name):
        self.id = id
        self.abbrev = abbrev
        self.name = name


class TeamScore(Team):
    def __init__(self, id, abbrev, name, goals=0, sog=0, penalties=None, powerplay=False, num_skaters=0, pulled_goalie=False, goal_plays=None):
        super().__init__(id, abbrev, name)
        if goal_plays is None:
            goal_plays = []
        if penalties is None:
            penalties = []
        self.goals = goals
        self.goal_plays = goal_plays
        self.shot_on_goal = sog
        self.penalties = penalties
        self.powerplay = powerplay
        self.num_skaters = num_skaters
        self.pulled_goalie = pulled_goalie


class SeriesTeam(Team):
    def __init__(self, matchupTeam, abbrev):
        super().__init__(matchupTeam["id"], abbrev, matchupTeam["name"]["default"])
        self.isTop = matchupTeam["seed"]
        self.rank = matchupTeam["seed"]
        self.series_wins = matchupTeam["seriesWins"]
        self.series_losses = matchupTeam["record"].split("-")[1]
