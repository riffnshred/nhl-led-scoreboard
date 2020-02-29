#class Standings:
#     def __init__(self, config):
#         self.config = config
#         self.conference()
#         self.division()
#
#     def conference(self):
#         conf = getattr(self.standing_data.by_conference, self.config.preferred_conference)
#         print(conf)
#
#     def division(self):
#         div = getattr(self.standing_data.by_division, self.config.preferred_divisions)
#         print(div)
#
#
#
#     # def render(self, data):
#     #     type = data.config.standing_type
#     #     if type == 'conference':
#     #         conf = getattr(data.standings.by_conference, self.config.preferred_conference)
#     #         print(conf)
#     #     elif type == 'division':
#     #         div = getattr(data.standings.by_division, self.config.preferred_divisions)
#     #         print(div)