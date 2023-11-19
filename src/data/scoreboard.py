from data.team import TeamScore
from data.periods import Periods
from utils import convert_time
from time import sleep
import debug

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
        if play.type_desc_key == "goal":
            scoring_plays.append(play)
        if play.type_desc_key == "penalty":
            penalty_plays.append(play)
    
    away_goal_plays = [ x for x in scoring_plays if x.details.event_owner_team_id == away_id]
    home_goal_plays = [ x for x in scoring_plays if x.details.event_owner_team_id == home_id]
    away_penalties = [ x for x in penalty_plays if x.details.event_owner_team_id == away_id]
    home_penalties = [ x for x in penalty_plays if x.details.event_owner_team_id == home_id]

    return away_goal_plays, away_penalties, home_goal_plays, home_penalties


def get_goal_players(play_details, roster, opposing_roster):
    """
        Grab the list of players involved in a goal and return their Id except for assists which is a list of Ids
    """
    scorer = {}
    assists = []
    goalie = {}
    
    scorer["info"] = roster[play_details.scoring_player_id]
    # Likely need to check if these are None first
    if play_details.assist_1_player_id:
        assists.append({"info": roster[play_details.assist_1_player_id]})
    if play_details.assist_2_player_id:
        assists.append({"info": roster[play_details.assist_2_player_id]})
    # Turns out if it's an empty net goal, there's no goalie in net
    if play_details.goalie_in_net_id:
        goalie = opposing_roster[play_details.goalie_in_net_id]

    return {"scorer":scorer, "assists":assists, "goalie":goalie}

def get_penalty_players(play_details, roster):
    player_id = ""
    if play_details.committed_by_player_id:
        player_id = play_details.committed_by_player_id
    if play_details.served_by_player_id:
        player_id = play_details.served_by_player_id
    return roster[player_id]

class Scoreboard:
    def __init__(self, overview, data):
        time_format = data.config.time_format
        # linescore = overview.linescore

        # away = linescore.teams.away
        away_team = overview.away_team
        away_team_id = away_team.id
        away_team_name = away_team.name
        away_abbrev = data.teams_info[away_team_id].details.abbrev

        # home = linescore.teams.home
        home_team = overview.home_team
        home_team_id = home_team.id
        home_team_name = home_team.name
        home_abbrev = data.teams_info[home_team_id].details.abbrev

        away_goal_plays = []
        home_goal_plays = []

        away_penalties = []
        home_penalties = []

        self.away_roster = {}
        self.home_roster = {}
        for player in overview.roster_spots:
            if player.team_id == home_team_id:
                self.home_roster[player.player_id] = player
            else:
                self.away_roster[player.player_id] = player

        home_skaters = 5
        away_skaters = 5
        if len(overview.plays) > 0:
            plays = overview.plays
            away_scoring_plays, away_penalty_plays, home_scoring_plays, home_penalty_plays = filter_plays(plays,away_team.id,home_team.id)
            
            # Get the Away Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in away_scoring_plays:
                # try:
                # print(play)
                players = get_goal_players(play.details, self.away_roster, self.home_roster)
                away_goal_plays.append(Goal(play, players))
                # except KeyError:
                    # debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                    # away_goal_plays = []
                    # break
            # Get the Home Goal details
            # If the request to the API fails or is missing who scorer and the assists are, return an empty list of goal plays
            # This method is there to prevent the goal board to display the wrong info
            for play in home_scoring_plays:
                # try:
                players = get_goal_players(play.details, self.home_roster, self.away_roster)
                home_goal_plays.append(Goal(play,players))
                # except KeyError:
                #     debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                #     home_goal_plays = []
                #     break

            for play in away_penalty_plays:
                # try:
                player = get_penalty_players(play.details, self.away_roster)
                away_penalties.append(Penalty(play, player))
                # except KeyError:
                #     debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                #     away_penalties = []
                #     break

            for play in home_penalty_plays:
                # try:
                player = get_penalty_players(play.details, self.home_roster)
                home_penalties.append(Penalty(play,player))
                # except KeyError:
                #     debug.error("Failed to get Goal details for current live game. will retry on data refresh")
                #     home_penalties = []
                #     break
        home_skaters = len(overview.home_team.on_ice)
        away_skaters = len(overview.away_team.on_ice)

        home_pp = False
        away_pp = False
        home_goalie_pulled = False
        away_goalie_pulled = False
        # TODO: I'm not entirely sure what's going on with situation
        try:
            if overview.situation:
                home_skaters = overview.situation.home_team.strength
                away_skaters = overview.situation.away_team.strength
                if overview.situation.home_team.situation_descriptions:
                    if "PP" in overview.situation.home_team.situation_descriptions:
                        home_pp = True
                    if "EN" in overview.situation.home_team.situation_descriptions:
                        home_goalie_pulled = True
                if overview.situation.away_team.situation_descriptions:
                    if "PP" in overview.situation.away_team.situation_descriptions:
                        away_pp = True
                    if "EN" in overview.situation.away_team.situation_descriptions:
                        away_goalie_pulled = True
        except:
            print(overview)
            exit()

        away_team_sog = away_team.sog if away_team.sog else 0
        home_team_sog = home_team.sog if home_team.sog else 0
        self.away_team = TeamScore(away_team_id, away_abbrev, away_team_name, overview.away_team.score, away_team_sog, away_penalties, away_pp, away_skaters, away_goalie_pulled, away_goal_plays)
        self.home_team = TeamScore(home_team_id, home_abbrev, home_team_name, overview.home_team.score, home_team_sog, home_penalties, home_pp, home_skaters, home_goalie_pulled, home_goal_plays)

        self.date = overview.game_date.strftime("%b %d")
        self.start_time = convert_time(overview.start_time_utc).strftime(time_format)
        self.status = overview.game_state
        self.periods = Periods(overview)
        self.intermission = overview.clock.in_intermission

        if overview.game_state == "OFF" or overview.game_state == "FINAL":
            if away_team.score > home_team.score:
                self.winning_team_id = overview.away_team.id
                self.winning_score = overview.away_team.score
                self.losing_team_id = overview.home_team.id
                self.losing_score = overview.home_team.score
            else:
                self.losing_team_id = overview.away_team.id
                self.losing_score = overview.away_team.score
                self.winning_team_id = overview.home_team.id
                self.winning_score = overview.home_team.score

    

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
        away_team = game_details.away_team
        away_team_id = away_team.id
        away_team_name = away_team.name
        away_abbrev = data.teams_info[away_team_id].details.abbrev

        # home = linescore.teams.home
        home_team = game_details.home_team
        home_team_id = home_team.id
        home_team_name = home_team.name
        home_abbrev = data.teams_info[home_team_id].details.abbrev

        self.away_team = TeamScore(away_team_id, away_abbrev, away_team_name, game_details.away_team.score)
        self.home_team = TeamScore(home_team_id, home_abbrev, home_team_name, game_details.home_team.score)

        self.date = game_details.game_date.strftime("%b %d")
        self.start_time = convert_time(game_details.start_time_utc).strftime(time_format)
        self.status = game_details.game_state
        self.periods = Periods(game_details)
        self.intermission = game_details.clock.in_intermission if game_details.clock else False

        if game_details.game_state == "OFF" or game_details.game_state == "FINAL":
            if game_details.away_team.score > game_details.home_team.score:
                self.winning_team_id = game_details.away_team.id
                self.winning_score = game_details.away_team.score
                self.losing_team_id = game_details.home_team.id
                self.losing_score = game_details.home_team.score
            else:
                self.losing_team_id = game_details.away_team.id
                self.losing_score = game_details.away_team.score
                self.winning_team_id = game_details.home_team.id
                self.winning_score = game_details.home_team.score

    

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
        self.team = play.details.event_owner_team_id
        self.period = play.period_descriptor.number
        self.periodTime = play.time_in_period
        
class Penalty:
    def __init__(self, play, player):
        self.player = player
        self.penaltyType = play.details.desc_key
        self.severity = play.details.type_code
        self.penaltyMinutes = str(play.details.duration)
        self.team_id = play.details.event_owner_team_id
        self.period = play.sort_order
        self.periodTime = play.time_in_period
