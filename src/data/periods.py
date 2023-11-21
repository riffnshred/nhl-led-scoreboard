class Periods:
    PLAYOFF = 'P'
    END = 'End'
    FINAL = 'Final'
    ORDINAL = ['Scheduled', '1st', '2nd', '3rd', 'OT', 'SO']
    ORDINAL_PLAYOFF = ['Scheduled', '1st', '2nd', '3rd', 'OT', '2OT', '3OT', '4OT', '5OT']

    def __init__(self, overview):
        self.is_intermission = overview.clock.in_intermission if overview.clock else False
        self.gameType = overview.game_type
        self.number = 0
        # Possible states. FUT, PRE, OFF, LIVE, CRIT, FINAL
        if overview.game_state == "LIVE" or overview.game_state == "CRIT":
            # Apparently the number can be nil? I am struggling figure out why this is failing
            self.number = overview.period_descriptor.number if overview.period_descriptor.number else 0

        try:
            self.clock = overview.clock.time_remaining
        except AttributeError:
            self.clock = '00:00'
        self.get_ordinal()

    def get_ordinal(self):
        if self.is_intermission:
            self.ordinal = "INT"
        elif self._is_playoff():
            self.ordinal = Periods.ORDINAL_PLAYOFF[self.number]
        else:
            self.ordinal = Periods.ORDINAL[self.number]

    def _is_playoff(self):
        return self.gameType is self.PLAYOFF
