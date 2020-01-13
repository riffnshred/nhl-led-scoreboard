"""
    Shows list of games.
    TODO:
        Make sliding animation.
"""
class Scoreticker:
    def __init__(self, data):
        self.data = data
        print(data.games[0].home_score)
