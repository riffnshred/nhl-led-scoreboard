import os
import threading

import debug
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options, stop_splash_service
from renderer.matrix import Matrix, TermMatrix
from config.files.layout import LayoutConfig
from config.files.fonts import FontsConfig
from utils import get_file
from PIL import ImageFont
from config.main import Config
import nhl_api 



class Data:
    def __init__(self, config):
        self.config = ConfigT()
        self.scoreboard = ScoreBoardTest()
        self.status = None
        self.team_colors = Color()
        self.pref_teams = [1]
        self.teams_info = nhl_api.info.team_info()

    def RetScoreboard(self):
        return self.scoreboard

class ConfigT():
    def __init__(self):
        self.goal_anim_pref_team_only = False
        self.live_game_refresh_rate = 10
        self.sog_display_frequency = 30
        self.layout = Layout()
        self.config = Config((64,32))
        self.team_colors = Color()

class Layout:
    def __init__(self):
        self.font = ImageFont.truetype(get_file("assets/fonts/04B_24__.TTF"),8)
        self.font_medium = ImageFont.truetype(get_file("assets/fonts/04B_24__.TTF"),16)


class ScoreBoardTest:
    def __init__(self):
        away_team_id = 2
        home_team_id = 1
        away_abbrev = "NYR"
        home_abbrev = "TOR"
        away_team_name = "Rangers"
        home_team_name = "Toronto"
        away_skaters = {}
        home_skaters = {}
        self.away_team = TeamScore(away_team_id,away_abbrev,away_team_name, 2, away_skaters)
        self.home_team = TeamScore(home_team_id,home_abbrev,home_team_name, 1, home_skaters)


class TeamScore:
    def __init__(self, team_id, abbrev, team_name, goals, skaters):
        self.id = team_id
        self.name = team_name
        self.goals = goals
        self.goal_plays = [Goal()]
        self.abbrev = abbrev
        self.penalties = [Penalty()]


class Boards:
    def __init__(self):
        self.what = None

class Color:
    def __init__(self):
        self.json = {'1': {'primary': {'r': 206, 'g': 17, 'b': 38}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '2': {'primary': {'r': 0, 'g': 83, 'b': 155}, 'text': {'r': 244, 'g': 125, 'b': 48}}, '3': {'primary': {'r': 0, 'g': 56, 'b': 168}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '4': {'primary': {'r': 247, 'g': 73, 'b': 2}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '5': {'primary': {'r': 252, 'g': 181, 'b': 20}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '6': {'primary': {'r': 252, 'g': 181, 'b': 20}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '7': {'primary': {'r': 0, 'g': 48, 'b': 135}, 'text': {'r': 243, 'g': 208, 'b': 62}}, '8': {'primary': {'r': 175, 'g': 30, 'b': 45}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '9': {'primary': {'r': 197, 'g': 32, 'b': 50}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '10': {'primary': {'r': 0, 'g': 32, 'b': 91}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '12': {'primary': {'r': 226, 'g': 24, 'b': 54}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '13': {'primary': {'r': 4, 'g': 30, 'b': 66}, 'text': {'r': 200, 'g': 16, 'b': 46}}, '14': {'primary': {'r': 0, 'g': 40, 'b': 104}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '15': {'primary': {'r': 4, 'g': 30, 'b': 66}, 'text': {'r': 200, 'g': 16, 'b': 46}}, '16': {'primary': {'r': 207, 'g': 10, 'b': 44}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '17': {'primary': {'r': 206, 'g': 17, 'b': 38}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '18': {'primary': {'r': 255, 'g': 184, 'b': 28}, 'text': {'r': 4, 'g': 30, 'b': 66}}, '19': {'primary': {'r': 0, 'g': 47, 'b': 135}, 'text': {'r': 252, 'g': 181, 'b': 20}}, '20': {'primary': {'r': 200, 'g': 16, 'b': 46}, 'text': {'r': 241, 'g': 190, 'b': 72}}, '21': {'primary': {'r': 111, 'g': 38, 'b': 61}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '22': {'primary': {'r': 4, 'g': 30, 'b': 66}, 'text': {'r': 252, 'g': 76, 'b': 0}}, '23': {'primary': {'r': 0, 'g': 32, 'b': 91}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '24': {'primary': {'r': 185, 'g': 151, 'b': 91}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '25': {'primary': {'r': 0, 'g': 104, 'b': 71}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '26': {'primary': {'r': 162, 'g': 170, 'b': 173}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '28': {'primary': {'r': 0, 'g': 109, 'b': 117}, 'text': {'r': 255, 'g': 255, 'b': 255}}, '29': {'primary': {'r': 0, 'g': 38, 'b': 84}, 'text': {'r': 164, 'g': 169, 'b': 173}}, '30': {'primary': {'r': 2, 'g': 73, 'b': 48}, 'text': {'r': 175, 'g': 35, 'b': 36}}, '52': {'primary': {'r': 4, 'g': 30, 'b': 66}, 'text': {'r': 142, 'g': 144, 'b': 144}}, '53': {'primary': {'r': 140, 'g': 38, 'b': 51}, 'text': {'r': 226, 'g': 214, 'b': 181}}, '54': {'primary': {'r': 185, 'g': 151, 'b': 91}, 'text': {'r': 0, 'g': 0, 'b': 0}}, '55': {'primary': {'r': 0, 'g': 22, 'b': 40}, 'text': {'r': 153, 'g': 217, 'b': 217}}, 'Eastern': {'primary': {'r': 196, 'g': 18, 'b': 18}, 'text': {'r': 0, 'g': 0, 'b': 0}}, 'Western': {'primary': {'r': 0, 'g': 62, 'b': 126}}, 'east': {'primary': {'r': 0, 'g': 140, 'b': 85}}, 'west': {'primary': {'r': 0, 'g': 98, 'b': 179}}, 'central': {'primary': {'r': 216, 'g': 102, 'b': 31}}, 'north': {'primary': {'r': 202, 'g': 24, 'b': 38}}}

    def color(self, keypath):
        try: 
            d = self.__find_at_keypath(keypath)
        except KeyError as e:
            raise e
        return d

    def __find_at_keypath(self,keypath):
        keys = keypath.split('.')
        rv = self.json
        for key in keys:
            rv = rv[key]
        return rv



class Goal:
    def __init__(self):
        self.scorer = {'info': {'teamId': 12, 'playerId': 8478970, 'firstName': {'default': "K'Andre"}, 'lastName': {'default': 'Lafrenière'}, 'sweaterNumber': 5, 'positionCode': 'D', 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/CAR/8478970.png'}}
        self.assists = [{'info': {'teamId': 12, 'playerId': 8480039, 'firstName': {'default': 'Martin'}, 'lastName': {'default': 'Stützle', 'cs': 'Nečas', 'sk': 'Nečas'}, 'sweaterNumber': 88, 'positionCode': 'C', 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/CAR/8480039.png'}}, {'info': {'teamId': 12, 'playerId': 8480835, 'firstName': {'default': 'Jack'}, 'lastName': {'default': 'Barré-Boule'}, 'sweaterNumber': 18, 'positionCode': 'C', 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/CAR/8480835.png'}}]
        self.periodTime = "14:44"
        self.period = 1
        self.team = 1

class Penalty:
    def __init__(self):
        self.team_id = 1
        self.player = {'teamId': 12, 'playerId': 8478970, 'firstName': {'default': 'Jalen'}, 'lastName': {'default': 'Lafrenière'}, 'sweaterNumber': 5, 'positionCode': 'D', 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/CAR/8478970.png'}
        self.periodTime = "14:44"
        self.penaltyMinutes = "2"
        self.severity = "Min"



def test_gp():

    stop_splash_service()
    commandArgs = args()

    if commandArgs.terminal_mode and sys.stdin.isatty():
        height,width = os.popen("stty size",'r').read().split()
        termMatrix = TermMatrix(int(width), int(height))
        matrix = Matrix(termMatrix)
    else:
        matrixOptions = led_matrix_options(commandArgs)
        matrixOptions.drop_privileges = False
        matrix = Matrix(RGBMatrix(options = matrixOptions))

    config = ScoreboardConfig("config", commandArgs, (matrix.width, matrix.height))

    data = Data(config)

    sleepEvent = threading.Event()
    
    renderer = MainRenderer(matrix, data, sleepEvent)
    
    renderer.test_setup(data)

    renderer.check_new_goals()

    renderer.check_new_penalty()



if __name__ == "__main__":
    test_gp()



