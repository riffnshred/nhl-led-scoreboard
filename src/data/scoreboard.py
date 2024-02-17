from data.team import TeamScore
from data.periods import Periods
from utils import convert_time
from time import sleep
import debug
from datetime import datetime
"""
    TODO:
        Split the current Scoreboard class into two:
            - scoreboard (subclass of game, only showing minimum data of a game like the status, score, away and home etc...  )
            - game (for the overview, load all the static data like players, away and home teams etc... on init 
            and have methods to refresh the dynamic data like score, goals, penalty etc...)

        This will affect how the Data module init and refresh games. Need to test figure what this change will affect.
"""

def filter_plays(plays, away_id, home_id):
    """
        Take a list of scoring plays and split them into their cooresponding team.
        return two list, one for each team.
    """
    scoring_plays = []
    penalty_plays = []
    away_goal_plays = []
    away_penalties  = []
    home_goal_plays = []
    home_penalties = []

    # Filter the scoring plays out of all the plays
    for play in plays:
        if play["typeDescKey"] == "goal":
            scoring_plays.append(play)
        if play["typeDescKey"] == "penalty":
            penalty_plays.append(play)
    
    away_goal_plays = [ x for x in scoring_plays if x["details"]["eventOwnerTeamId"] == away_id]
    home_goal_plays = [ x for x in scoring_plays if x["details"]["eventOwnerTeamId"] == home_id]
    away_penalties = [ x for x in penalty_plays if x["details"]["eventOwnerTeamId"] == away_id]
    home_penalties = [ x for x in penalty_plays if x["details"]["eventOwnerTeamId"] == home_id]

    return away_goal_plays, away_penalties, home_goal_plays, home_penalties


def get_goal_players(play_details, roster, opposing_roster):
    """
        Grab the list of players involved in a goal and return their Id except for assists which is a list of Ids
    """
    scorer = {}
    assists = []
    goalie = {}
    
    scorer["info"] = roster[play_details["scoringPlayerId"]]
    # Likely need to check if these are None first
    if play_details.get("assist1PlayerId"):
        assists.append({"info": roster[play_details["assist1PlayerId"]]})
    if play_details.get("assist2PlayerId"):
        assists.append({"info": roster[play_details["assist2PlayerId"]]})
    # Turns out if it's an empty net goal, there's no goalie in net
    if play_details.get("goalieInNetId"):
        goalie = opposing_roster[play_details["goalieInNetId"]]
    elif not play_details.get("goalieInNetId"):
        goalie = 'ON'

    return {"scorer":scorer, "assists":assists, "goalie":goalie}

def get_penalty_players(play_details, roster):
    player_id = ""
    if play_details.get("committedByPlayerId"):
        player_id = play_details["committedByPlayerId"]
    if play_details.get("servedByPlayerId"):
        player_id = play_details["servedByPlayerId"]
    return roster[player_id]

class Scoreboard:
    def __init__(self, overview, data):
        time_format = data.config.time_format
        # linescore = overview.linescore

        # away = linescore.teams.away
        away_team = overview["awayTeam"]
        away_team_id = away_team["id"]
        away_team_name = away_team["name"]["default"]
        away_abbrev = data.teams_info[away_team_id].details.abbrev

        # home = linescore.teams.home
        home_team = overview["homeTeam"]
        home_team_id = home_team["id"]
        home_team_name = home_team["name"]["default"]
        home_abbrev = data.teams_info[home_team_id].details.abbrev

        away_goal_plays = []
        home_goal_plays = []

        away_penalties = []
        home_penalties = []

        self.away_roster = {}
        self.home_roster = {}
        for player in overview["rosterSpots"]:
            if player["teamId"] == home_team_id:
                self.home_roster[player["playerId"]] = player
            else:
                self.away_roster[player["playerId"]] = player

        home_skaters = 5
        away_skaters = 5
        if len(overview["plays"]) > 0:
            plays = overview["plays"]
            away_scoring_plays, away_penalty_plays, home_scoring_plays, home_penalty_plays = filter_plays(plays,away_team_id,home_team_id)
            
            # Get the Away Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in away_scoring_plays:
                try:
                # print(play)
                    players = get_goal_players(play["details"], self.away_roster, self.home_roster)
                    away_goal_plays.append(Goal(play, players))
                except KeyError:
                    debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                    away_goal_plays = []
                    break
            # Get the Home Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in home_scoring_plays:
                try:
                    players = get_goal_players(play["details"], self.home_roster, self.away_roster)
                    home_goal_plays.append(Goal(play,players))
                except KeyError:
                    debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                    home_goal_plays = []
                    break

            for play in away_penalty_plays:
                try:
                    player = get_penalty_players(play["details"], self.away_roster)
                    away_penalties.append(Penalty(play, player))
                except KeyError:
                     debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                     away_penalties = []
                     break

            for play in home_penalty_plays:
                try:
                    player = get_penalty_players(play["details"], self.home_roster)
                    home_penalties.append(Penalty(play,player))
                except KeyError:
                     debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                     home_penalties = []
                     break
        home_skaters = len(overview["homeTeam"]["onIce"])
        away_skaters = len(overview["awayTeam"]["onIce"])

        home_pp = False
        away_pp = False
        home_goalie_pulled = False
        away_goalie_pulled = False

        # TODO: I'm not entirely sure what's going on with situation
        try:
            if overview.get("situation"):
                home_skaters = overview["situation"]["homeTeam"]["strength"]
                away_skaters = overview["situation"]["awayTeam"]["strength"]
                if overview["situation"]["homeTeam"].get("situationDescriptions"):
                    if "PP" in overview["situation"]["homeTeam"]["situationDescriptions"]:
                        home_pp = True
                    if "EN" in overview["situation"]["homeTeam"]["situationDescriptions"]:
                        home_goalie_pulled = True
                if overview["situation"]["awayTeam"].get("situationDescriptions"):
                    if "PP" in overview["situation"]["awayTeam"]["situationDescriptions"]:
                        away_pp = True
                    if "EN" in overview["situation"]["awayTeam"]["situationDescriptions"]:
                        away_goalie_pulled = True
            else:
                debug.info("No situation data")
        except:
            debug.info("Situation Load Error")
            exit()

        away_team_sog = away_team["sog"] if away_team.get("sog") else 0
        home_team_sog = home_team["sog"] if home_team.get("sog") else 0
        self.away_team = TeamScore(away_team_id, away_abbrev, away_team_name, overview["awayTeam"]["score"], away_team_sog, away_penalties, away_pp, away_skaters, away_goalie_pulled, away_goal_plays)
        self.home_team = TeamScore(home_team_id, home_abbrev, home_team_name, overview["homeTeam"]["score"], home_team_sog, home_penalties, home_pp, home_skaters, home_goalie_pulled, home_goal_plays)
    
        self.date = datetime.strptime(overview["gameDate"],'%Y-%m-%d').strftime("%b %d")
        self.start_time = convert_time(datetime.strptime(overview["startTimeUTC"],'%Y-%m-%dT%H:%M:%SZ')).strftime(time_format)
        self.status = overview["gameState"]
        self.periods = Periods(overview)
        self.intermission = overview["clock"]["inIntermission"]

        if overview["gameState"] == "OFF" or overview["gameState"] == "FINAL":
            if away_team["score"] > home_team["score"]:
                self.winning_team_id = overview["awayTeam"]["id"]
                self.winning_score = overview["awayTeam"]["score"]
                self.losing_team_id = overview["homeTeam"]["id"]
                self.losing_score = overview["homeTeam"]["score"]
            else:
                self.losing_team_id = overview["awayTeam"]["id"]
                self.losing_score = overview["awayTeam"]["score"]
                self.winning_team_id = overview["homeTeam"]["id"]
                self.winning_score = overview["homeTeam"]["score"]

    

    def __str__(self):
        output = "<{} {}> {} (G {}, SOG {}) @ {} (G {}, SOG {}); Status: {}; Period : {} {};".format(
            self.__class__.__name__, hex(id(self)),
            self.away_team.name, str(self.away_team.goals), str(self.away_team.shot_on_goal),
            self.home_team.name, str(self.home_team.goals), str(self.home_team.shot_on_goal),
            self.status,
            self.periods.ordinal,
            self.periods.clock
        )
        return output

class GameSummaryBoard:
    def __init__(self, game_details, data):
        time_format = data.config.time_format
        # linescore = overview.linescore

        # away = linescore.teams.away
        away_team = game_details["awayTeam"]
        away_team_id = away_team["id"]
        if away_team.get("name"):
            away_team_name = away_team["name"]["default"]
        elif away_team.get("placeName"):
            away_team_name = away_team["placeName"]["default"]
        away_abbrev = data.teams_info[away_team_id].details.abbrev

        # home = linescore.teams.home
        home_team = game_details["homeTeam"]
        home_team_id = home_team["id"]
        if home_team.get("name"):
            home_team_name = home_team["name"]["default"]
        elif home_team.get("placeName"):
            home_team_name = home_team["placeName"]["default"]
        home_abbrev = data.teams_info[home_team_id].details.abbrev

        if game_details["homeTeam"].get("score") or game_details["awayTeam"].get("score"):
            self.away_team = TeamScore(away_team_id, away_abbrev, away_team_name, game_details["awayTeam"]["score"])
            self.home_team = TeamScore(home_team_id, home_abbrev, home_team_name, game_details["homeTeam"]["score"])
        else:
            self.away_team= TeamScore(away_team_id, away_abbrev, away_team_name, 0)
            self.home_team = TeamScore(home_team_id, home_abbrev, home_team_name, 0)


        self.date = datetime.strptime(game_details["gameDate"], '%Y-%m-%d').strftime("%b %d")
        self.start_time = convert_time(datetime.strptime(game_details["startTimeUTC"],'%Y-%m-%dT%H:%M:%SZ')).strftime(time_format)
        self.status = game_details["gameState"]
        self.periods = Periods(game_details)
        try:
            self.intermission = game_details["clock"]["inIntermission"] if game_details["clock"] else False
        except KeyError:
            self.intermission = False

        if game_details["gameState"] == "OFF" or game_details["gameState"] == "FINAL":
            if game_details["awayTeam"]["score"] > game_details["homeTeam"]["score"]:
                self.winning_team_id = game_details["awayTeam"]["id"]
                self.winning_score = game_details["awayTeam"]["score"]
                self.losing_team_id = game_details["homeTeam"]["id"]
                self.losing_score = game_details["homeTeam"]["score"]
            else:
                self.losing_team_id = game_details["awayTeam"]["id"]
                self.losing_score = game_details["awayTeam"]["score"]
                self.winning_team_id = game_details["homeTeam"]["id"]
                self.winning_score = game_details["homeTeam"]["score"]

    

    def __str__(self):
        output = "<{} {}> {} (G {}, SOG {}) @ {} (G {}, SOG {}); Status: {}; Period : {} {};".format(
            self.__class__.__name__, hex(id(self)),
            self.away_team.name, str(self.away_team.goals), str(self.away_team.shot_on_goal),
            self.home_team.name, str(self.home_team.goals), str(self.home_team.shot_on_goal),
            self.status,
            self.periods.ordinal,
            self.periods.clock
        )
        return output

class Goal:
    def __init__(self, play, players):
        self.scorer = players["scorer"]
        self.assists = players["assists"]
        self.goalie = players["goalie"]
        self.team = play["details"]["eventOwnerTeamId"]
        self.period = play["periodDescriptor"]["number"]
        self.periodTime = play["timeInPeriod"]
        
class Penalty:
    def __init__(self, play, player):
        self.player = player
        self.penaltyType = play["details"]["descKey"]
        self.severity = play["details"]["typeCode"]
        self.penaltyMinutes = str(play["details"]["duration"])
        self.team_id = play["details"]["eventOwnerTeamId"]
        self.period = play["periodDescriptor"]["number"]
        self.periodTime = play["timeInPeriod"]
