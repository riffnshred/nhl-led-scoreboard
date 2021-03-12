class Periods:
    PLAYOFF = 'P'
    END = 'End'
    FINAL = 'Final'
    ORDINAL = ['Scheduled', '1st', '2nd', '3rd', 'OT', 'SO']
    ORDINAL_PLAYOFF = ['Scheduled', '1st', '2nd', '3rd', 'OT', '2OT', '3OT', '4OT', '5OT']

    def __init__(self, overview):
        period_info = overview.linescore
        try:
            intermission_info = period_info.intermissionInfo
            self.is_intermission = intermission_info.inIntermission
            self.intermission_time_remaining = intermission_info.intermissionTimeRemaining
        except AttributeError:
            self.is_intermission = False

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
