import nhl_api.data
from nhl_api.object import Object, MultiLevelObject
import debug


def team_info():
    """
        Returns a list of team information dictionaries
    """
    data = nhl_api.data.get_teams()
    parsed = data.json()
    teams_data = parsed["teams"]
    teams = []

    for team in teams_data:
        team_id = team['id']
        name = team['name']
        abbreviation = team['abbreviation']
        team_name = team['teamName']
        location_name = team['locationName']
        short_name = team['shortName']
        division_id = team['division']['id']
        division_name = team['division']['name']
        #division_abbrev = team['division']['abbreviation']
        conference_id = team['conference']['id']
        conference_name = team['conference']['name']
        official_site_url = team['officialSiteUrl']
        franchise_id = team['franchiseId']

        try:
            previous_game = team['previousGameSchedule']
            # previous_game = False
        except:
            debug.log("No next game detected for {}".format(team_name))
            previous_game = False

        try:
            next_game = team['nextGameSchedule']
        except:
            debug.log("No next game detected for {}".format(team_name))
            next_game = False

        try:
            stats = team['teamStats'][0]['splits'][0]['stat']
        except:
            debug.log("No Stats detected for {}".format(team_name))
            stats = False

        output = {
            'team_id': team_id,
            'name': name,
            'abbreviation': abbreviation,
            'team_name': team_name,
            'location_name': location_name,
            'short_name': short_name,
            'division_id': division_id,
            'division_name': division_name,
            #'division_abbrev': division_abbrev,
            'conference_id': conference_id,
            'conference_name': conference_name,
            'official_site_url': official_site_url,
            'franchise_id': franchise_id,
            'previous_game': previous_game,
            'next_game': next_game,
            'stats': stats
        }

        # put this dictionary into the larger dictionary
        teams.append(output)

    return teams

def player_info(playerId):
    data = nhl_api.data.get_player(playerId)
    parsed = data.json()
    player = parsed["people"][0]

    return MultiLevelObject(player)

def status():
    data = nhl_api.data.get_game_status().json()
    return data


def current_season():
    data = nhl_api.data.get_current_season().json()
    return data


def playoff_info(season):
    data = nhl_api.data.get_playoff_data(season)
    parsed = data.json()
    season = parsed["season"]
    output = {'season': season}
    try:
        playoff_rounds = parsed["rounds"]
        rounds = {}
        for r in range(len(playoff_rounds)):
            rounds[str(playoff_rounds[r]["number"])] = MultiLevelObject(playoff_rounds[r])
        
        output['rounds'] = rounds
    except KeyError:
        debug.error("No data for {} Playoff".format(season))
        output['rounds'] = False

    try:
        default_round = parsed["defaultRound"]
        output['default_round'] = default_round
    except KeyError:
        debug.error("No default round for {} Playoff.".format(season))
        default_round = 0
        output['default_round'] = default_round

    return output

def series_record(seriesCode, season):
    data = data = nhl_api.data.get_series_record(seriesCode, season)
    parsed = data.json()
    return parsed["data"]

def standings():
    standing_records = {}

    # wildcard_records = {
    #     'eastern': [],
    #     'western': []
    # }

    data = nhl_api.data.get_standings().json()
    divisions = data['records']

    #data_wildcard = nhl_api.data.get_standings_wildcard().json()
    #wildcard = data_wildcard['records']
    for division in range(len(divisions)):
        team_records = divisions[division]['teamRecords']
        division_full_name = divisions[division]['division']['name'].split()
        division_name = division_full_name[-1]
        #conference_name = divisions[division]['conference']['name']

        for team in range(len(team_records)):
            team_id = team_records[team]['team']['id']
            team_name = team_records[team]['team']['name']
            team_records[team].pop('team')
            standing_records[team_id] = {
                'division': division_name,
                #'conference': conference_name,
                'team_name': team_name,
                'team_id': team_id
            }
            for key, value in team_records[team].items():
                standing_records[team_id][key] = value

    # for record in wildcard:
    #     if record['conference']['name'] == 'Eastern':
    #         wildcard_records['eastern'].append(record)
    #     elif record['conference']['name'] == 'Western':
    #         wildcard_records['western'].append(record)

    #return standing_records, wildcard_records
    return standing_records

class Standings(object):
    """
        Object containing all the standings data per team.

        Contains functions to return a dictionary of the data reorganised to represent
        different type of Standings.

    """
    def __init__(self, records):
        self.data = records
        #self.data_wildcard = wildcard
        #self.get_conference()
        self.get_division()
        #self.get_wild_card()

    # def get_conference(self):
    #     eastern, western = self.sort_conference(self.data)
    #     self.by_conference = nhl_api.info.Conference(eastern, western)

    # def get_division(self):
    #     metropolitan, atlantic, central, pacific = self.sort_division(self.data)
    #     self.by_division = nhl_api.info.Division(metropolitan, atlantic, central, pacific)

    def get_division(self):
        west, east, north, central = self.sort_division(self.data)
        self.by_division = nhl_api.info.Division(west, east, north, central)

    # def get_wild_card(self):
    #     """
    #         This function take the wildcard data from the API and turn them into objects.
    #         TODO:
    #             the way I wrote this function is not pythonic at all (but works). Need to rewrite this part.
    #     """
    #     conferences_data = self.data_wildcard
    #     eastern = []
    #     western = []
    #     for conference in conferences_data:
    #         """ Reset variables """
    #         metropolitan = []
    #         atlantic = []
    #         central = []
    #         pacific = []
    #         wild_card = []
    #         for record in conferences_data[conference]:
    #             if record['standingsType'] == "wildCard":
    #                 wild_card = record['teamRecords']
    #             elif record['standingsType'] == "divisionLeaders":
    #                 if record['division']['name'] == "Metropolitan":
    #                     metropolitan = record
    #                 elif record['division']['name'] == "Atlantic":
    #                     atlantic = record
    #                 elif record['division']['name'] == "Central":
    #                     central = record
    #                 elif record['division']['name'] == "Pacific":
    #                     pacific = record

    #         division = nhl_api.info.Division(metropolitan, atlantic, central, pacific)

    #         if conference == 'eastern' and wild_card and division:
    #             eastern = nhl_api.info.Wildcard(wild_card, division)
    #         elif conference == 'western':
    #             western = nhl_api.info.Wildcard(wild_card, division)

    #     self.by_wildcard = nhl_api.info.Conference(eastern, western)

    def _league(self):
        pass

    # @staticmethod
    # def sort_conference(data):
    #     eastern = []
    #     western = []
    #     for item in data:
    #         if data[item]['conference'] == 'Eastern':
    #             eastern.append(data[item])

    #         elif data[item]['conference'] == 'Western':
    #             western.append(data[item])

    #     eastern = sorted(eastern, key=lambda i: int(i['conferenceRank']))
    #     western = sorted(western, key=lambda i: int(i['conferenceRank']))
    #     return eastern, western

    @staticmethod
    def sort_division(data):
        west = []
        east = []
        north = []
        central = []

        for item in data:
            if data[item]['division'] == 'West':
                west.append(data[item])

            elif data[item]['division'] == 'East':
                east.append(data[item])

            elif data[item]['division'] == 'Central':
                central.append(data[item])

            elif data[item]['division'] == 'North':
                north.append(data[item])

        west = sorted(west, key=lambda i: int(i['conferenceRank']))
        east = sorted(east, key=lambda i: int(i['conferenceRank']))
        central = sorted(central, key=lambda i: int(i['conferenceRank']))
        north = sorted(north, key=lambda i: int(i['conferenceRank']))

        return west, east, north, central


# class Conference:
#     def __init__(self, east, west):
#         if east:
#             self.eastern = east
#         if west:
#             self.western = west


class Division:
    def __init__(self, w, e, n, c):
        if w:
            self.west = w
        if e:
            self.east = e
        if n:
            self.north = n
        if c:
            self.central = c


# class Wildcard:
#     def __init__(self, wild, div):
#         self.wild_card = wild
#         self.division_leaders = div


class Playoff():
    def __init__(self, data):
        self.season = data['season']
        self.default_round = data['default_round']
        self.rounds = data['rounds']

    def __str__(self):
        return (f"Season: {self.season}, Current round: {self.default_round}")

    def __repr__(self):
        return self.__str__()

class Info(nhl_api.object.Object):
    pass