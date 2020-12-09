import nhl_api

class Game:
    """
    Contains all the data of a game.
    """
    def __init__(self, info, overview=None):
        self.id = info.id
        self.status = ""

        if overview != None:
            self.linescore = overview.linescore
            self.gameType = overview.game_type

        # Initialize the time stamp. The time stamp is found only in the live feed endpoint of a game in the API
        # It shows the last time (UTC) the data was updated. EX 20200114_041103
        self.time_stamp = "00000000_000000"
    
    def update(overview)


class Period:
    def __init__(self):
        PLAYOFF = 'P'
        END = 'End'
        FINAL = 'Final'
        ORDINAL = ['Scheduled', '1st', '2nd', '3rd', 'OT', 'SO']
        ORDINAL_PLAYOFF = ['Scheduled', '1st', '2nd', '3rd', 'OT', '2OT', '3OT', '4OT', '5OT']

    def __init__(self, overview):
        period_info = overview.linescore
        intermission_info = period_info.intermissionInfo
        self.is_intermission = intermission_info.inIntermission
        self.intermission_time_remaining = intermission_info.intermissionTimeRemaining
        self.gameType = overview.game_type
        self.number = period_info.currentPeriod
        try:
            self.clock = period_info.currentPeriodTimeRemaining
        except AttributeError:
            self.clock = '00:00'
        self.get_ordinal()

    def get_ordinal(self):
        if self._is_playoff():
            self.ordinal = Periods.ORDINAL_PLAYOFF[self.number]
        else:
            self.ordinal = Periods.ORDINAL[self.number]

    def _is_playoff(self):
        return self.gameType is self.PLAYOFF