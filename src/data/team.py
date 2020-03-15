class Team:
    def __init__(self, id, abbrev, name, goals=0, sog=0, powerplay=False, num_skaters=0, pulled_goalie=False):
        self.id = id
        self.abbrev = abbrev
        self.name = name
        self.goals = goals
        self.shot_on_goal = sog
        self.powerplay = powerplay
        self.num_skaters = num_skaters
        self.pulled_goalie = pulled_goalie