from nhl_api.object import MultiLevelObject
import nhl_api.data
import debug

"""
    TODO: For some reason the playoff data became to heavy and the recursion loop to transform the data into a single class
      - Change the playoff class to multiple subclass and distribute different types of data into different types of object.

    For now it only pickup what the software need from the API.
"""

def playoff_info():
    data = nhl_api.data.get_playoff_data()
    parsed = data.json()
    playoff_rounds = parsed["rounds"]

    season = parsed["season"]
    default_round = parsed["defaultRound"]
    output = {'season':season, 'default_round':default_round}
    rounds = []

    for index in range(len(playoff_rounds)):
      for x in playoff_rounds[index]:
          rounds.append(MultiLevelObject(playoff_rounds[index]))

    output['rounds'] = rounds
    return output


class Playoff():
    def __init__(self, data):
        self.season = data['season']
        self.default_round = data['default_round']
        self.rounds = data['rounds']
    
    def __str__(self):
        return (f"{self.rounds[0].series[0].matchupTeams[0].seed.rank}")

    def __repr__(self):
        return self.__str__()




"""
API playoff sample from : 
https://statsapi.web.nhl.com/api/v1/tournaments/playoffs?expand=round.series,schedule.game.seriesSummary&season=20182019


"id" : 1,
"name" : "Playoffs",
"season" : "20182019",
"defaultRound" : 4,

"rounds" : [ {
    "number" : 1,
    "code" : 1,
    "names" : {
      "name" : "First Round",
      "shortName" : "R1"
    },
    "format" : {
      "name" : "BO7",
      "description" : "Best of 7",
      "numberOfGames" : 7,
      "numberOfWins" : 4
    },
    "series" : [ {
      "seriesNumber" : 1,
      "seriesCode" : "A",
      "names" : {
        "matchupName" : "Lightning (A1) vs. Blue Jackets (WC2)",
        "matchupShortName" : "TBL v CBJ",
        "teamAbbreviationA" : "TBL",
        "teamAbbreviationB" : "CBJ",
        "seriesSlug" : "lightning-vs-blue-jackets-series-a"
      },
      "currentGame" : {
        "seriesSummary" : {
          "gamePk" : 2018030114,
          "gameNumber" : 4,
          "gameLabel" : "Game 4",
          "necessary" : true,
          "gameCode" : 114,
          "gameTime" : "2019-04-16T23:00:00Z",
          "seriesStatus" : "CBJ 4-0, will face BOS",
          "seriesStatusShort" : "CBJ wins 4-0"
        }
      },
      "conference" : {
        "id" : 6,
        "name" : "Eastern",
        "link" : "/api/v1/conferences/6"
      },
      "round" : {
        "number" : 1
      },
      "matchupTeams" : [ {
        "team" : {
          "id" : 14,
          "name" : "Tampa Bay Lightning",
          "link" : "/api/v1/teams/14"
        },
        "seed" : {
          "type" : "1",
          "rank" : 1,
          "isTop" : true
        },
        "seriesRecord" : {
          "wins" : 0,
          "losses" : 4
        }
      }, {
        "team" : {
          "id" : 29,
          "name" : "Columbus Blue Jackets",
          "link" : "/api/v1/teams/29"
        },
        "seed" : {
          "type" : "WC2",
          "rank" : 4,
          "isTop" : false
        },
        "seriesRecord" : {
          "wins" : 4,
          "losses" : 0
        }
      } ]
    }
} ]

"""
