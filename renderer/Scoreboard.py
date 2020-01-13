class Scoreboard:
    def __init__(self, scoreboard):
        self.scoreboard = scoreboard

    def render(self):
        show = 'Showing scoreboard {0}'.format(self.scoreboard)
        print(show)