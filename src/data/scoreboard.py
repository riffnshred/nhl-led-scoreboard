from data.team import TeamScore
from data.periods import Periods
from utils import convert_time
import nhl_api


def filter_scoring_plays(plays, away_id, home_id):
    """
        Take a list of scoring plays and split them into their cooresponding team.
        return two list, one for each team. 
    """
    all_plays = plays.allPlays
    scoring_plays_id = plays.scoringPlays
    scoring_plays = []
    away = []
    home = []

    # Filter the scoring plays out of all the plays
    for i in scoring_plays_id:
        scoring_plays.append(all_plays[i])

    away = [ x for x in scoring_plays if x['team']['id'] == away_id]
    home = [ x for x in scoring_plays if x['team']['id'] == home_id]

    return away, home

def get_goal_players(players_list):
    """
        Grab the list of players involved in a goal and return their Id except for assists which is a list of Ids
    """
    scorerId = ""
    assistsId = ""
    goalieId = ""
    scorer = {}
    assists = []
    goalie = {}
    for player in players_list:
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                if player["playerType"] == "Scorer":
                    scorerId = player['player']['id']
                    scorer = nhl_api.player(scorerId)
                if player["playerType"] == "Assist":
                    assistsId = player['player']['id']
                    assists.append(nhl_api.player(assistsId)) 
                if player["playerType"] == "Goalie":
                    goalieId = player['player']['id']
                    goalie = nhl_api.player(goalieId)

                break
            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to get the players info related to a GOAL. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)
    
    return scorer, assists, goalie
            

class Scoreboard:
    def __init__(self, overview, data):
        time_format = data.config.time_format
        linescore = overview.linescore
        away = linescore.teams.away
        home = linescore.teams.home
        away_abbrev = data.teams_info[away.team.id].abbreviation
        home_abbrev = data.teams_info[home.team.id].abbreviation

        away_goal_plays = []
        home_goal_plays = []

        if hasattr(overview,"plays"):
            plays = overview.plays
            away_scoring_plays, home_scoring_plays = filter_scoring_plays(plays,away.team.id,home.team.id)
            for play in away_scoring_plays:
                away_goal_plays.append(Goal(play))
            for play in home_scoring_plays:
                home_goal_plays.append(Goal(play))

        self.away_team = TeamScore(away.team.id, away_abbrev, away.team.name, away.goals, away.shotsOnGoal, away.powerPlay,
                              away.numSkaters, away.goaliePulled, away_goal_plays)
        self.home_team = TeamScore(home.team.id, home_abbrev, home.team.name, home.goals, home.shotsOnGoal, home.powerPlay,
                              home.numSkaters, home.goaliePulled, home_goal_plays)

        self.date = convert_time(overview.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(overview.game_date).strftime(time_format)
        self.status = overview.status
        self.periods = Periods(overview)
        self.intermission = linescore.intermissionInfo.inIntermission

        if data.status.is_final(overview.status):
            self.winning_team = overview.w_team
            self.winning_score = overview.w_score
            self.loosing_team = overview.l_team
            self.loosing_score = overview.l_score

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
    def __init__(self, play):
        players = play['players']
        self.scorer, self.assists, self.goalie = get_goal_players(players)
        self.team = play['team']['id']
        self.period = play['about']['ordinalNum']
        self.periodTime = play['about']['periodTime']
        self.strength = play['result']['strength']['name']
        


        
