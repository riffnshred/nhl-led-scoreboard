import questionary
from questionary import Validator, ValidationError, prompt
from styles import custom_style_dope
from validate_json import validateConf
from print import *
import argparse
import functools
import regex
import re
import json
import os
import sys
import shutil


from time import sleep

SCRIPT_VERSION = "1.6.3"

TEAMS = ['Avalanche','Blackhawks','Blues','Blue Jackets','Bruins','Canadiens','Canucks','Capitals','Coyotes','Devils','Ducks','Flames','Flyers',
    'Golden Knights','Hurricanes','Islanders','Jets','Kings','Kraken','Maple Leafs','Lightning','Oilers','Panthers','Penguins','Predators',
    'Rangers','Red Wings','Sabres','Senators','Sharks','Stars','Wild']

#Everything that can be configured in the config.json
SECTIONS = ['general','preferences','states','boards','sbio']
STATES = ['off_day','scheduled','intermission','post_game']
#the boards listed below are what's listed in the config
# These are boards that have configuration.  If your board does not have any config, you don't need to add it
BOARDS = ['clock','weather','wxalert','scoreticker','seriesticker','standings']
SBIO = ['pushbutton','dimmer','screensaver']

def getVersion():
    
    workingDir = os.getcwd()
    versionFile = os.path.join(workingDir,'VERSION')
    version = '0.0.0'
    #Get installed version by reading VERSION file located in cwd
    if os.path.exists(versionFile):
        try:
            with open(versionFile) as verFile:
                version = verFile.read().strip()
        except OSError:
            print("Unable to open {}".format(versionFile))
    else:
        print("File {} does not exist.".format(versionFile))
        
    return version

class Clock24hValidator(Validator):
    def validate(self, document):
        ok = regex.match('^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid time in 24 hour format',
                cursor_position=len(document.text))  # Move cursor to end

class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end

class RGBValidator(Validator):
    def validate(self, document):
        r = r"(\d+),\s*(\d+),\s*(\d+)"
        #ok = regex.match('^(\d+),\s*(\d+),\s*(\d+)$', document.text)
        ok = False
        if re.match(r,document.text) is not None:
            ok = all(0 <= int(group) <= 255 for group in re.match(r, document.text).groups())
        if not ok:
            raise ValidationError(
                message='Please enter a valid RGB tuple (r,g,b)',
                cursor_position=len(document.text))  # Move cursor to end


def get_file(path):
    dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(dir, path)

# Attempt to load a configuration file from config directory to use as defaults for prompts
# If config.json exists (user already created one, or this app has already been ran) use it,
# If no config.json exists, look for config.json.sample and if that doesn't exist, create a new config.json
# If simple = True, force the config file to be the config.json.sample as we are setting up with defaults

def load_config(confdir,simple=False):
    # Find and return a json file

        filename = ["config.json","config.json.sample",".default/config.json.sample"]
        j = {}

        jloaded = False

        if simple:
            fileindex = 1
        else:
            fileindex = 0

        while not jloaded:

            if fileindex >= len(filename):
                jloaded = True
            else:
                path = get_file("{0}/{1}".format(confdir,filename[fileindex]))

            if os.path.isfile(path):
                try:
                    j = json.load(open(path))
                    jloaded = True
                except json.decoder.JSONDecodeError as e:
                    div.div('*')
                    print("Unable to load json: {0}".format(e),BOLD,RED)
                    div.div('*')
                    sys.exit(os.EX_NOINPUT)
            else:
                fileindex += 1

        return j

def save_config(nhl_config,confdir):
    savefile = json.dumps(nhl_config, sort_keys=False, indent=4)
    #Make backup of original file if exists
    #Check if directory exists
    if not os.path.exists(confdir):
        #os.makedirs(confdir)
        print("Directory {} does not exist.  Are you running in the right directory?".format(confdir),RED)
        sys.exit(os.EX_OSFILE)
    try:
        shutil.copyfile("{}/config.json".format(confdir),"{}/config.json.backup".format(confdir))
    except Exception as e:
        print("Could not make backup of {0}/config.json. This is normal for first run".format(confdir),CYAN)
        print("Message: {0}".format(e),YELLOW)

    try:
        with open('{}/config.json'.format(confdir),'w') as f:
            try:
                f.write(savefile)
            except Exception as e:
                print("Could not write {0}/config.json. Error Message: {1}".format(confdir,e),RED)
    except Exception as e:
        print("Could not open {0} directory, unable to save config.json. Error Message: {1}".format(confdir,e),RED)


def get_default_value(def_config,def_key,def_type):
    if def_config:
        res = functools.reduce(lambda val, key: val.get(key) if val else None, def_key, def_config) 
        if def_type == "int":
            return str(res)
        return res
    else:
        if def_type == "bool":
            return True
        else:
            return ""

def select_teams(qmark):
    team_select_answer = [
        {
            'type': 'confirm',
            'name': 'team_select',
            'qmark': qmark,
            'message': 'Add another team?',
            'default': True
        }
    ]
    answer = prompt(team_select_answer)

    return answer['team_select']

def select_boards(qmark):
    board_select_answer = [
        {
            'type': 'confirm',
            'name': 'board_select',
            'qmark': qmark,
            'message': 'Add another board?',
            'default': True
        }
    ]
    answer = prompt(board_select_answer)

    return answer['board_select']

def get_team(team_index,team_choices,pref_teams,qmark):

    def_choices = TEAMS

    choices = []

    if len(pref_teams) >= 0 and len(team_choices) > 0:
        #Combine lists with teams from team_choices first
        choices = [ele for ele in def_choices if ele not in team_choices]
        if len(pref_teams) > 0:
            choices = [ele for ele in def_choices if ele not in pref_teams]
        choices = team_choices + choices

    if len(pref_teams) > 0 and len(team_choices) == 0:
        # Remove anything all ready selected from the choices list
        choices = [ele for ele in def_choices if ele not in pref_teams]

    if len(pref_teams) == 0 and len(team_choices) == 0:
        choices = def_choices

    if team_index == 0:
        message = "Select your preferred team:"
    else:
        message = "Select a team:"

    team_prompt = [
        {
            'type': 'list',
            'name': 'team',
            'qmark': qmark,
            'message': message,
            'choices': choices,
        }
    ]
    answers = prompt(team_prompt,style=custom_style_dope)
    return answers['team']

def get_board(state,boardlist,qmark):

    message ='Select a board to display for ' + state
    states_prompt = [
        {
            'type': 'list',
            'name': 'board',
            'qmark': qmark,
            'message': message,
            'choices': boardlist,
        }
    ]
    answers = prompt(states_prompt,style=custom_style_dope)
    return answers['board']

def general_settings(default_config,qmark):

    questions = [

        {
            'type': 'confirm',
            'name': 'debug',
            'qmark': qmark,
            'message': 'Do you want full debug on (only use this if asked to)? (outputs ALL log messages to console)',
            'default': get_default_value(default_config,['debug'],"bool")
        },
        {
            'type' : 'list',
            'name' : 'loglevel',
            'qmark': qmark,
            'message' : "What log level do you want? ",
            "when": lambda x: not x["debug"],
            'choices' : ['INFO','WARNING','ERROR','CRITICAL'],
            'default' : get_default_value(default_config,['loglevel'],"string") or 'INFO'
        },
        {
            'type': 'confirm',
            'name': 'live_mode',
            'qmark': qmark,
            'message': 'Do you want live_mode on? (Shows live game data of favorite team)',
            'default': get_default_value(default_config,['live_mode'],"bool")
        }
    ]

    return prompt(questions, style=custom_style_dope)

def preferences_settings(default_config,qmark):
    preferences = {'preferences':{}}
    time_format = [
        {
        'type' : 'list',
        'name' : 'time_format',
        'qmark': qmark,
        'message' : "Select the time format",
        'choices' : ['12h','24h'],
        'default' : get_default_value(default_config,['preferences','time_format'],"string") or '12h'
        }
    ]
    get_time_format = prompt(time_format,style=custom_style_dope)

    preferences['preferences']=get_time_format

    end_of_day = [
        {
            'type': 'input',
            'name': 'end_of_day',
            'qmark': qmark,
            'message': 'When do you want end of day to be?',
            'validate': Clock24hValidator,
            'default': get_default_value(default_config,['preferences','end_of_day'],"string") or '12:00'
        }
    ]
    get_eod = prompt(end_of_day,style=custom_style_dope)
    preferences['preferences'].update(get_eod)

    location = [
        {
            'type': 'input',
            'name': 'location',
            'qmark': qmark,
            'message': 'Your location to override latitude and longitude lookup via IP (City, State or City, Province or lat,lon or home address)',
            'default': get_default_value(default_config,['preferences','location'],"string")
        }
    ]
    get_location = prompt(location,style=custom_style_dope)
    preferences['preferences'].update(get_location)

    refresh_rate = [
        {
            'type': 'input',
            'name': 'live_game_refresh_rate',
            'qmark': qmark,
            'message': 'Live game refresh rate? (rate at which a live game will call the NHL API to catch the new data, 10 seconds is the lowest)',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 10 else 'Must be a number and greater than 10',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['preferences','live_game_refresh_rate'],"int") or '15'
        }
    ]
    get_refresh = prompt(refresh_rate,style=custom_style_dope)

    preferences['preferences'].update(get_refresh)

    selected_teams = get_default_value(default_config,['preferences','teams'],"string")
    preferences_teams = []

    team_index=0
    team = None
    team = get_team(team_index,selected_teams,preferences_teams,qmark)

    if len(selected_teams) > 0 and (team in selected_teams):
        selected_teams.remove(team)

    preferences_teams.append(team)
    team_select = select_teams(qmark)

    while team_select:
        team_index += 1
        team = get_team(team_index,selected_teams,preferences_teams,qmark)
        if len(selected_teams) > 0 and (team in selected_teams):
            selected_teams.remove(team)
        preferences_teams.append(team)
        team_select = select_teams(qmark)

    preferences_team_dict = {'teams':preferences_teams}
    preferences['preferences'].update(preferences_team_dict)

    sog_display = [
        {
            'type': 'input',
            'name': 'sog_display_frequency',
            'qmark': qmark,
            'message': 'SOG Display Frequency? (How often do you want to see shots on goal)',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 2 else 'Must be a number and greater than 2',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['preferences','sog_display_frequency'],"int") or '4'
        }
    ]
    get_sog = prompt(sog_display,style=custom_style_dope)

    preferences['preferences'].update(get_sog)

    goal_animations_dict ={'goal_animations':{}}

    questions = [

        {
            'type': 'confirm',
            'name': 'pref_team_only',
            'qmark': qmark,
            'message': 'Do you want goal animations for only preferred team?',
            'default': get_default_value(default_config,['preferences','goal_animations','pref_team_only'],"bool")
        },
    ]

    goal_animation_answer = prompt(questions,style=custom_style_dope)
    goal_animations_dict['goal_animations'].update(goal_animation_answer)


    preferences['preferences'].update(goal_animations_dict)

    return preferences

def states_settings(default_config,qmark,setup_type):
    states = STATES
    temp_dict = {}

    # States configuration
    states_config = get_default_value(default_config,['states'],"string")
    #Select the boards you want to update
    if setup_type != "full":
        thestates = (
            questionary.checkbox(
                "Select states(s) to configure (no selection defaults to all states)", choices=STATES, style=custom_style_dope,qmark=qmark
            ).ask()
            or STATES
        )
    else:
        thestates = STATES

    for astate in thestates:
        board_list = ['clock','weather','wxalert','wxforecast','scoreticker','seriesticker','standings','team_summary','stanley_cup_champions','christmas','seasoncountdown']

        boards_selected = []
        board = None
        select_board = True

        while select_board:
            board = get_board(astate,board_list,qmark)
            boards_selected.append(board)
            board_list.remove(board)
            if len(board_list) != 0:
                select_board = select_boards(qmark)
            else:
                select_board=False


        if astate == 'off_day':
            states_config['off_day'] = boards_selected
        if astate == 'scheduled':
            states_config['scheduled'] = boards_selected
        if astate == 'intermission':
            states_config['intermission'] = boards_selected
        if astate == 'post_game':
            states_config['post_game'] = boards_selected


    states_dict = {'states':{}}
    states_dict['states'].update(states_config)

    return states_dict

# Put the settings for each board here, one function per board

def scoreticker(default_config,qmark):
    # Get scoreticker config
    scoreticker_default = get_default_value(default_config,['boards','scoreticker'],"string")

    scoreticker_questions = [
        {
            'type': 'confirm',
            'name': 'preferred_teams_only',
            'qmark': qmark,
            'message': 'Score Ticker: Show preferred teams only? (Show only your preferred team or all games of the day)',
            'default': get_default_value(default_config,['boards','scoreticker','preferred_teams_only'],"bool")
        },
        {
            'type': 'input',
            'name': 'rotation_rate',
            'qmark': qmark,
            'message': 'Score Ticker: Board rotation rate? (How often do you want to rotate the games shown)',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['boards','scoreticker','rotation_rate'],"int") or '5'
        }
    ]

    scoreticker_conf = prompt(scoreticker_questions,style=custom_style_dope)

    scoreticker_default.update(scoreticker_conf)

    return scoreticker_default

def seriesticker(default_config,qmark):
    # Get seriesticker config
    seriesticker_default = get_default_value(default_config,['boards','seriesticker'],"string")

    seriesticker_questions = [
        {
            'type': 'confirm',
            'name': 'preferred_teams_only',
            'qmark': qmark,
            'message': 'Series Ticker: Show preferred teams only? (Show only your preferred team or all the series of the playoff)',
            'default': get_default_value(default_config,['boards','seriesticker','preferred_teams_only'],"bool")
        },
        {
            'type': 'input',
            'name': 'rotation_rate',
            'qmark': qmark,
            'message': 'Series Ticker: Board rotation rate? (How often do you want to rotate the series shown)',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['boards','seriesticker','rotation_rate'],"int") or '5'
        }
    ]

    seriesticker_conf = prompt(seriesticker_questions,style=custom_style_dope)

    seriesticker_default.update(seriesticker_conf)

    return seriesticker_default

def standings(default_config,qmark):

    standings_default = get_default_value(default_config,['boards','standings'],"string")

    standings_questions = [
        {
            'type': 'confirm',
            'name': 'preferred_standings_only',
            'qmark': qmark,
            'message': 'Show preferred standings only? (Show all standings or your preferred division and conference)',
            'default': get_default_value(default_config,['boards','standings','preferred_standings_only'],"bool")
        },
        {
            'type' : 'list',
            'name' : 'standing_type',
            'qmark': qmark,
            'message' : "Select the type of standings to display",
            'choices' : ['conference','division','wild_card'],
            'default' : get_default_value(default_config,['boards','standings','standing_type'],"string") or 'conference'
        },
        {
            'type' : 'list',
            'name' : 'divisions',
            'qmark': qmark,
            'message' : "Select the division to display",
            'choices' : ['atlantic','metropolitan','central','pacific'],
            'default' : get_default_value(default_config,['boards','standings','divisions'],"string") or 'atlantic'
        },
        {
            'type' : 'list',
            'name' : 'conference',
            'qmark': qmark,
            'message' : "Select the conference to display",
            'choices' : ['eastern','western'],
            'default' : get_default_value(default_config,['boards','standings','conference'],"string") or 'eastern'
        }
    ]

    standings_conf = prompt(standings_questions,style=custom_style_dope)

    standings_default.update(standings_conf)

    return standings_default

def clock(default_config,qmark):
    clock_default = get_default_value(default_config,['boards','clock'],"string")

    clock_questions = [
        {
            'type': 'input',
            'name': 'duration',
            'qmark': qmark,
            'message': 'Duration clock is shown',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['boards','clock','duration'],"int") or '60'
        },
        {
            'type': 'confirm',
            'name': 'hide_indicator',
            'qmark': qmark,
            'message': 'Hide network indicator when clock displayed (for when there are network issues, red bar on bottom of display)',
            'default': get_default_value(default_config,['boards','clock','hide_indicator'],"bool")
        },
        {
            'type': 'confirm',
            'name': 'preferred_team_colors',
            'qmark': qmark,
            'message': "Use your first preferred team's colors for clock and date?",
            'default': get_default_value(default_config,['boards','clock','preferred_team_colors'],"bool")
        },
        {
            'type': 'input',
            'name': 'clock_rgb',
            'qmark': qmark,
            'message': 'Set the clock numbers to the RGB value if preferred_team_colors set to false.  format: 0,0,0',
            "when": lambda x: not x["preferred_team_colors"],
            'validate': RGBValidator,
            'default': get_default_value(default_config,['boards','clock','clock_rgb'],"string") or '255,255,255'
        },
        {
            'type': 'input',
            'name': 'date_rgb',
            'qmark': qmark,
            'message': 'Set the date, weather and AM/PM numbers to the RGB value if preferred_team_colors set to false.  format: 0,0,0',
            "when": lambda x: not x["preferred_team_colors"],
            'validate': RGBValidator,
            'default': get_default_value(default_config,['boards','clock','date_rgb'],"string") or '255,255,255'
        },
        {
            'type': 'confirm',
            'name': 'flash_seconds',
            'qmark': qmark,
            'message': "Flash seconds?",
            'default': get_default_value(default_config,['boards','clock','flash_seconds'],"bool")
        },
    ]

    clock_conf = prompt(clock_questions,style=custom_style_dope)

    clock_default.update(clock_conf)

    return clock_default

def weather(default_config,qmark):

    #Add weather info
    #Get default config
    wx_default = get_default_value(default_config,['boards','weather'],"string")
    wx_enabled = [
        {
            'type': 'confirm',
            'name': 'enabled',
            'qmark': qmark,
            'message': 'Use weather data feed (this is required to get data for the weather and weather alert boards)?',
            'default': get_default_value(default_config,['boards','weather','enabled'],"bool") or True
        }
    ]

    use_wx = prompt(wx_enabled,style=custom_style_dope)

    if use_wx['enabled']:
        wx = True
        wx_default.update(enabled = wx)

        wx_questions = [

                {
                    'type': 'input',
                    'name': 'units',
                    'qmark': qmark,
                    'message': 'Units to display? (metric or imperial)',
                    'default': get_default_value(default_config,['boards','weather','units'],"string") or "metric"
                },
                {
                    'type': 'input',
                    'name': 'update_freq',
                    'qmark': qmark,
                    'validate': lambda val: True if val.isdecimal() and int(val) >= 5 else 'Must be a number and greater or equal than 5',
                    'filter': lambda val: int(val),
                    'message': 'How often to update weather in minutes?(minimum 5)',
                    'default': get_default_value(default_config,['boards','weather','update_freq'],"int") or '5'
                },
                {
                    'type': 'list',
                    'name': 'view',
                    'qmark': qmark,
                    'message': 'Weather observation display',
                    'choices': ['full','summary'],
                    'default': get_default_value(default_config,['boards','weather','view'],"string") or "full"
                },
                {
                    'type': 'input',
                    'name': 'duration',
                    'qmark': qmark,
                    'validate': lambda val: True if val.isdecimal() and int(val) >= 30 else 'Must be at least 30 seconds',
                    'filter': lambda val: int(val),
                    'message': 'How long to show weather board (minimum 30 seconds)?',
                    'default': get_default_value(default_config,['boards','weather','duration'],"int") or '30'
                },
                {
                    'type': 'list',
                    'name': 'data_feed',
                    'qmark': qmark,
                    'choices': ['EC','OWM'],
                    'message': 'Which weather data feed for current observations? EC=Environment Canada\nOWM=Open Weather Map (requires a key: works for all locations)',
                    'default': get_default_value(default_config,['boards','weather','data_feed'],"string") or 'EC'
                },
                {
                    'type': 'input',
                    'name': 'owm_apikey',
                    'qmark': qmark,
                    'message': 'OpenWeatherMap API key if using OWM as data feed: (get key from https://openweathermap.org/appid)',
                    "when": lambda x: x["data_feed"] == 'OWM',
                    'default': get_default_value(default_config,['boards','weather','owm_apikey'],"string") or ''
                },
                {
                'type': 'confirm',
                'name': 'show_on_clock',
                'qmark': qmark,
                'message': 'Display temperature and humidity on clock?',
                'default': get_default_value(default_config,['boards','weather','show_on_clock'],"bool") or True
                },
                {
                'type': 'confirm',
                'name': 'forecast_enabled',
                'qmark': qmark,
                'message': 'Get weather forecast from your weather provider?',
                'default': get_default_value(default_config,['boards','weather','forecast_enabled'],"bool") or True
                },
                {
                    'type': 'input',
                    'name': 'forecast_days',
                    'qmark': qmark,
                    'validate': lambda val: True if val.isdecimal() and int(val) >= 1 and int(val) <= 3 else 'Must be a number and greater or equal than 1 and less than or equal to 3',
                    'filter': lambda val: int(val),
                    "when": lambda x: x["forecast_enabled"],
                    'message': 'Number of days forecast to show?(minimum 1, max 3)',
                    'default': get_default_value(default_config,['boards','weather','forecast_days'],"int") or '1'
                },
                {
                    'type': 'input',
                    'name': 'forecast_update',
                    'qmark': qmark,
                    'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
                    'filter': lambda val: int(val),
                    "when": lambda x: x["forecast_enabled"],
                    'message': 'How often to update weather forecast in hours?(minimum 1)',
                    'default': get_default_value(default_config,['boards','weather','forecast_update'],"int") or '1'
                },
            ]

        wx_conf = prompt(wx_questions,style=custom_style_dope)
        wx_default.update(wx_conf)
    else:
        wx = False
        wx_default.update(enabled = wx)

    return wx_default

def wxalert(default_config,qmark):
        #Get default config
    alerts_default = get_default_value(default_config,['boards','wxalert'],"string")

    alerts_enabled = [
        {
            'type': 'confirm',
            'name': 'show_alerts',
            'qmark': qmark,
            'message': 'Show weather alerts?',
            'default': get_default_value(default_config,['boards','wxalert','show_alerts'],"bool") or True
            }
    ]

    use_alerts = prompt(alerts_enabled,style=custom_style_dope)

    if use_alerts['show_alerts']:
        alerts = True

        alerts_default.update(show_alerts= alerts)

        alerts_questions = [
            {
                'type': 'list',
                'name': 'alert_feed',
                'qmark': qmark,
                'choices': ['EC','NWS'],
                'message': 'Which weather feed for alerts? EC=Environment Canada\nNWS=National Weather Service (US only)',
                'default': get_default_value(default_config,['boards','wxalert','alert_feed'],"string") or 'EC'
            },
            {
            'type': 'confirm',
            'name': 'alert_title',
            'qmark': qmark,
            'message': 'On alert board, display title of alert (warning, watch, advisory)?',
            'default': get_default_value(default_config,['boards','wxalert','alert_title'],"bool") or True
            },
            {
            'type': 'confirm',
            'name': 'nws_show_expire',
            'qmark': qmark,
            'message': 'For NWS alert feed use expire time rather than effective time?',
            "when": lambda x: x["alert_feed"] == 'NWS',
            'default': get_default_value(default_config,['boards','wxalert','nws_show_expire'],"bool") or True
            },
            {
            'type': 'confirm',
            'name': 'scroll_alert',
            'qmark': qmark,
            'message': 'On alert board, scroll alert?',
            'default': get_default_value(default_config,['boards','wxalert','scroll_alert'],"bool") or True
            },
            {
                'type': 'input',
                'name': 'alert_duration',
                'qmark': qmark,
                'validate': lambda val: True if val.isdecimal() and int(val) >= 5 else 'Must be a number and greater or equal than 5',
                'filter': lambda val: int(val),
                'message': 'How long (in seconds) to show the alert board',
                'default': get_default_value(default_config,['boards','wxalert','alert_duration'],"int") or '5'
            },
            {
                'type': 'input',
                'name': 'update_freq',
                'qmark': qmark,
                'validate': lambda val: True if val.isdecimal() and int(val) >= 5 else 'Must be a number and greater or equal than 5',
                'filter': lambda val: int(val),
                'message': 'How often to update alert feed in minutes?(minimum 5)',
                'default': get_default_value(default_config,['boards','wxalert','update_freq'],"int") or '5'
            },
            {
            'type': 'confirm',
            'name': 'show_on_clock',
            'qmark': qmark,
            'message': 'Display alert notification (Fred) on clock?',
            'default': get_default_value(default_config,['boards','wxalert','show_on_clock'],"bool") or True
            },

        ]

        alerts_answers = prompt(alerts_questions,style=custom_style_dope)
        alerts_default.update(alerts_answers)

    else:
        alerts = False
        alerts_default.update(show_alerts= alerts)

    return alerts_default

def board_settings(default_config,qmark,setup_type):
    # Boards configuration
    boards_config = get_default_value(default_config,['boards'],"string")

    #Select the boards you want to update
    if setup_type != "full":
        theboards = (
            questionary.checkbox(
                "Select board(s) to configure (no selection defaults to all boards)", choices=BOARDS, style=custom_style_dope,qmark=qmark
            ).ask()
            or BOARDS
        )
    else:
        theboards = BOARDS

    for aboard in theboards:
        if aboard == 'scoreticker':
            boards_config['scoreticker'] = scoreticker(default_config,qmark)
        if aboard == 'seriesticker':
            boards_config['seriesticker'] = seriesticker(default_config,qmark)
        if aboard == 'standings':
            boards_config['standings'] = standings(default_config,qmark)
        if aboard == 'clock':
            boards_config['clock'] = clock(default_config,qmark)
            #boards_config.update(clock(default_config,qmark))
        if aboard == 'weather':
            boards_config['weather'] = weather(default_config,qmark)
        if aboard == 'wxalert':
            boards_config['wxalert'] = wxalert(default_config,qmark)

    #boards_dict = {'boards':{}}
    #boards_dict = boards_config

    return boards_config

# SBIO boards go here
def dimmer(default_config,qmark):

    dimmer_default = get_default_value(default_config,['sbio','dimmer'],"string")
    dimmer_enabled = [
        {
            'type': 'confirm',
            'name': 'enabled',
            'qmark': qmark,
            'message': 'Use dimmer',
            'default': get_default_value(default_config,['sbio','dimmer','enabled'],"bool")
        }
    ]

    use_dimmer = prompt(dimmer_enabled,style=custom_style_dope)
    if use_dimmer['enabled']:

        dimmer_default.update(use_dimmer)

        #Get all of the settings for the dimmer from the user
        dimmer_questions = [
            {
                'type' : 'list',
                'name' : 'source',
                'qmark': qmark,
                'message' : "Select source of dimmer, software (uses your IP to find sunrise/sunset) or hardware (a sensor attached)",
                'choices' : ['software','hardware'],
                'default' : get_default_value(default_config,['sbio','dimmer','source'],"string") or 'software'
            },
            {
                'type': 'input',
                'name': 'frequency',
                'qmark': qmark,
                'message': 'Frequency in minutes to check if dimming should happen',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','dimmer','frequency'],"int") or '5'
            },
            {
                'type': 'input',
                'name': 'light_level_lux',
                'qmark': qmark,
                'message': 'Level of light if a sensor is used to change brightness at (full daylight would be around 1000)',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 1 and int(val) <= 1000 else 'Must be a number between 1 and 1000',
                'filter': lambda val: int(val),
                "when": lambda x: x["source"] == "hardware",
                'default': get_default_value(default_config,['sbio','dimmer','light_level_lux'],"int") or '300'
            },
            {
                'type' : 'list',
                'name' : 'mode',
                'qmark': qmark,
                'message' : "When to allow dimming, always or only on off days",
                'choices' : ['always','off_day'],
                'default' : get_default_value(default_config,['sbio','dimmer','mode'],"string")
            },
            {
                'type': 'input',
                'name': 'sunset_brightness',
                'qmark': qmark,
                'message': 'How bright the display should be at night (between 5 and 100)',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 5 and int(val) <= 100 else 'Must be a number between 5 and 100',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','dimmer','sunset_brightness'],"int") or '5'
            },
            {
                'type': 'input',
                'name': 'sunrise_brightness',
                'qmark': qmark,
                'message': 'How bright the display should be during the day  (between 5 and 100)',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 5 and int(val) <= 100 else 'Must be a number between 5 and 100',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','dimmer','sunrise_brightness'],"int") or '40'
            }
        ]

        dimmer_answers = prompt(dimmer_questions,style=custom_style_dope)
        dimmer_default.update(dimmer_answers)

        #Check if user wants to override sunrise/sunset 

        if questionary.confirm("Override automatic sunrise/sunset with set times?",style=custom_style_dope,qmark=qmark).ask():
            override_questions = [
                {
                    'type': 'input',
                    'name': 'daytime',
                    'qmark': qmark,
                    'message': "When do you want the dimmer to start day time? (24h)",
                    'validate': Clock24hValidator,
                    'default': get_default_value(default_config,['sbio','dimmer','daytime'],"string") or '8:00'
                },
                {
                    'type': 'input',
                    'name': 'nighttime',
                    'qmark': qmark,
                    'message': "When do you want the dimmer to start night time? (24h)",
                    'validate': Clock24hValidator,
                    'default': get_default_value(default_config,['sbio','dimmer','nighttime'],"string") or '20:00'
                }
            ]
            override_answers = prompt(override_questions,style=custom_style_dope)
            dimmer_default.update(override_answers)
            dimmer_default.update(offset = 0)
        else:
            dimmer_default.update(daytime = "")
            dimmer_default.update(nighttime = "")

            if questionary.confirm("Add offset in minutes to automatic sunrise/sunset? (+ value adds to time, - subtracts from time",style=custom_style_dope,qmark=qmark).ask():
                offset_question = [
                    {
                    'type': 'input',
                    'name': 'offset',
                    'qmark': qmark,
                    'message': 'Offset in minutes to sunrise/sunset',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val),
                    'default': get_default_value(default_config,['sbio','dimmer','offset'],"int") or '0'
                    }
                ]
                offset_answer = prompt(offset_question,style=custom_style_dope)
                dimmer_default.update(offset_answer)
            else:
                dimmer_default.update(offset = 0)


    else:
        dimmer_default.update(enabled = False)
        #dimmer_default.update(sbio_default)

    return dimmer_default

def pushbutton(default_config,qmark):
    pb_default = get_default_value(default_config,['sbio','pushbutton'],"string")
    pb_enabled = [
        {
            'type': 'confirm',
            'name': 'enabled',
            'qmark': qmark,
            'message': 'Use pushbutton',
            'default': get_default_value(default_config,['sbio','pushbutton','enabled'],"bool")
        }
    ]
    use_pb = prompt(pb_enabled,style=custom_style_dope)
    if use_pb['enabled']:
        pb_default.update(enabled = True)
        #Get all of the settings for the pushbutton from the user
        pb_questions = [
            {
                'type' : 'confirm',
                'name' : 'bonnet',
                'qmark': qmark,
                'message' : "Are you using an Adafruit RGB Bonnet?",
                'default' : get_default_value(default_config,['sbio','pushbutton','bonnet'],"bool") or True
            },
            {
                'type': 'input',
                'name': 'pin',
                'qmark': qmark,
                'message': 'GPIO Pin button is connected to?',
                'validate': lambda val: True if val.isdecimal() and int(val) in [2,3,7,8,9,10,11,14,15,19,24,25] else 'Must be pin 2,3,7,8,9,10,11,14,15,19,24,25',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','pushbutton','pin'],"int") or '25'
            },
            {
                'type': 'input',
                'name': 'reboot_duration',
                'qmark': qmark,
                'message': 'How long button is held to trigger a reboot (must be less than power off duration)',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 2 else 'Must be at least 2 seconds',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','pushbutton','reboot_duration'],"int") or '2'
            },
            {
                'type': 'input',
                'name': 'reboot_override_process',
                'qmark': qmark,
                'message': 'Process (with full path and no arguments) to override /sbin/reboot?',
                'default': get_default_value(default_config,['sbio','pushbutton','reboot_override_process'],"string") or ''
            },
            {
                'type' : 'confirm',
                'name' : 'display_reboot',
                'qmark': qmark,
                'message' : "Display a REBOOT screen when reboot triggered?",
                'default' : get_default_value(default_config,['sbio','pushbutton','display_reboot'],"bool") or True
            },
            {
                'type': 'input',
                'name': 'poweroff_duration',
                'qmark': qmark,
                'message': 'How long button is held to trigger a poweroff (must be greater than reboot duration)',
                'validate': lambda val: True if val.isdecimal() and int(val) >= 2 else 'Must be at least 2 seconds',
                'filter': lambda val: int(val),
                'default': get_default_value(default_config,['sbio','pushbutton','poweroff_duration'],"int") or '10'
            },
            {
                'type': 'input',
                'name': 'poweroff_override_process',
                'qmark': qmark,
                'message': 'Process (with full path and no arguments) to override /sbin/poweroff?',
                'default': get_default_value(default_config,['sbio','pushbutton','poweroff_override_process'],"string") or ''
            },
            {
                'type' : 'confirm',
                'name' : 'display_halt',
                'qmark': qmark,
                'message' : "Display a HALT screen when reboot triggered?",
                'default' : get_default_value(default_config,['sbio','pushbutton','display_halt'],"bool") or True
            },
            {
                'type': 'list',
                'name': 'state_triggered1',
                'qmark': qmark,
                'message': 'Pick board to display on button press: ',
                'choices': ['clock','weather','wxalert','scoreticker','seriesticker','standings','team_summary'],
                'default': get_default_value(default_config,['sbio','pushbutton','state_triggered1'],"string") or 'clock'
            },
            {
                'type': 'input',
                'name': 'state_triggered1_process',
                'qmark': qmark,
                'message': 'Process (with full path and no arguments) to run on button press?',
                'default': get_default_value(default_config,['sbio','pushbutton','state_triggered1_process'],"string") or ''
            }
        ]

        pb_answers = prompt(pb_questions,style=custom_style_dope)
        pb_default.update(pb_answers)
    else:
        pb_default.update(enabled = False)
        #pb_default.update(sbio_default)

    return pb_default

def screensaver(default_config,qmark):
    ss_default = get_default_value(default_config,['sbio','screensaver'],"string")
    ss_enabled = [
        {
            'type': 'confirm',
            'name': 'enabled',
            'qmark': qmark,
            'message': 'Use screensaver',
            'default': get_default_value(default_config,['sbio','screensaver','enabled'],"bool")
        }
    ]
    use_ss = prompt(ss_enabled,style=custom_style_dope)
    if use_ss['enabled']:
        ss_default.update(enabled = True)
        #Get all of the settings for the pushbutton from the user
        ss_questions = [
            {
                'type' : 'confirm',
                'name' : 'animations',
                'qmark': qmark,
                'message' : "Use animations stored in assets/animations/screensaver?",
                'default' : get_default_value(default_config,['sbio','screensaver','animations'],"bool") or True
            },
            {
                'type': 'input',
                'name': 'start',
                'qmark': qmark,
                'message': "When do you want to start the screensaver? (24h)",
                'validate': Clock24hValidator,
                'default': get_default_value(default_config,['sbio','screensaver','start'],"string") or '21:00'
            },
            {
                'type': 'input',
                'name': 'stop',
                'qmark': qmark,
                'message': "When do you want the dimmer to stop the screensaver? (24h)",
                'validate': Clock24hValidator,
                'default': get_default_value(default_config,['sbio','screensaver','stop'],"string") or '08:00'
            },
            {
                'type': 'confirm',
                'name': 'data_updates',
                'qmark': qmark,
                'message': 'Update data feeds while screensaver is on? (applies to all weather feeds and dimmer, nhl will always be blocked with screensaver on)',
                'default': get_default_value(default_config,['sbio','screensaver','data_updates'],"bool")
            },
            {
                'type': 'confirm',
                'name': 'motionsensor',
                'qmark': qmark,
                'message': 'Use motion sensor to stop/start screensaver?',
                'default': get_default_value(default_config,['sbio','screensaver','motionsensor'],"bool")
            },
            {
                'type': 'input',
                'name': 'pin',
                'qmark': qmark,
                'message': 'Which GPIO pin is motion sensor attached to?',
                'validate': lambda val: True if val.isdecimal() and int(val) in [2,3,7,8,9,10,11,14,15,19,24,25] else 'Must be pin 2,3,7,8,9,10,11,14,15,19,24,25',
                'filter': lambda val: int(val),
                "when": lambda x: x["motionsensor"],
                'default': get_default_value(default_config,['sbio','screensaver','pin'],"int") or '24'
            },
            {
                'type': 'input',
                'name': 'delay',
                'qmark': qmark,
                'message': 'How long to wait for no motion?',
                'validate': NumberValidator,
                'filter': lambda val: int(val),
                "when": lambda x: x["motionsensor"],
                'default': get_default_value(default_config,['sbio','screensaver','delay'],"int") or '30'
            }
        ]

        ss_answers = prompt(ss_questions,style=custom_style_dope)
        ss_default.update(ss_answers)
    else:
        ss_default.update(enabled = False)
        #pb_default.update(sbio_default)
    return ss_default

def sbio_settings(default_config,qmark,setup_type):
    # SBIO configuration
    #sbio_config = {'sbio':{'dimmer':{},'pushbutton':{},'screensaver':{}}}
    sbio_config = get_default_value(default_config,['sbio'],"string")

    #Select the sbio you want to update
    if setup_type != "full":
        thesbio = (
            questionary.checkbox(
                "Select sbio section(s) to configure (no selection defaults to all sections)", choices=SBIO, style=custom_style_dope,qmark=qmark
            ).ask()
            or SBIO
        )
    else:
        thesbio = SBIO

    for asbio in thesbio:
        if asbio == 'dimmer':
            sbio_config['dimmer'] = dimmer(default_config,qmark)
        if asbio == 'pushbutton':
            sbio_config['pushbutton'] = pushbutton(default_config,qmark)
        if asbio == 'screensaver':
            sbio_config['screensaver'] = screensaver(default_config,qmark)

    return sbio_config

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('confdir', nargs='?',default="config", type=str, help='Input dir for config.json (defaults to config)')
    parser.add_argument('--version','-v', action='version', version='%(prog)s ' + SCRIPT_VERSION)
    parser.add_argument('--team','-t',nargs=1, action='store',type=str,help="Create simple config.json with defaults and one team")
    parser.add_argument('--simple','-s',action='store_true',help="Launch simple setup directly")
    parser.add_argument('--check','-c',action='store_true',help="Check config.json against schema, used to see if config is out of date")
    args = parser.parse_args()

    if not args.simple:
        print("NHL LED SCOREBOARD SETUP", SMSLANT,RED, BOLD)
        setupVersion="nhl_setup V{}".format(SCRIPT_VERSION)
        print(setupVersion,UNDERLINE,BLUE)
        mainVersion="nhl led scoreboard V{}".format(getVersion())
        print(mainVersion,UNDERLINE,GREEN,BOLD)
        
    if not os.path.exists(args.confdir):
        # Get current working directory
        setup_cwd = os.getcwd()
        print("Directory {0}/{1} does not exist.  Are you running in the right directory?".format(setup_cwd,args.confdir),RED)
        sys.exit(os.EX_OSFILE)

    #Check to see if the user wants to validate an existing config.json against the schema
    #Only from command line

    #Change to check on running app every time, if config is not valid, exit.

    #Check for existence of config/.default/firstrun file, if one exists, don't try to validate

    firstrun = "{0}/.default/firstrun".format(args.confdir)
    if not args.simple:
        if not os.path.exists(firstrun):
            conffile = "{0}/config.json".format(args.confdir)
            schemafile = "{0}/config.schema.json".format(args.confdir)
            if not os.path.exists(schemafile):
                schemafile = "{0}/.default/config.schema.json".format(args.confdir)

            confpath = get_file(conffile)
            schemapath = get_file(schemafile)
            print("Now validating config......")
            (valid,msg) = validateConf(confpath,schemapath)
            if valid:
                print("Your config.json passes validation and can be used with nhl led scoreboard",GREEN)
            else:
                print("Your config.json fails validation: error: [{0}]".format(msg),RED)
                sys.exit(os.EX_CONFIG)
            
            if args.check:
                sys.exit(0)
        else:
            os.remove(firstrun)

    #Check to see if there was a team name on the command line, if so, create a new config.json from
    #config.json.sample
    if args.team != None:
        default_config = load_config(args.confdir,True)
        # Make sure that the argument for the team supplied is valid
        if args.team[0] in TEAMS:
            default_config['preferences']['teams'] = args.team
            save_config(default_config,args.confdir)
        else:
            print("Your team {0} is not in {1}.  Check the spelling and try again".format(args.team[0],TEAMS),RED)
        sys.exit(os.EX_CONFIG)
    else:
        default_config = load_config(args.confdir)


    if questionary.confirm("Do you see a net,stick and horn?",style=custom_style_dope,qmark='🥅🏒🚨').skip_if(args.simple,default=True).ask():
        qmark = '🥅'
        qmarksave = '🥅🏒🚨'
    else:
        qmark = '?'
        qmarksave = '===>'

    if questionary.confirm("Do you want a simple default setup with one team selection (Y)?",style=custom_style_dope,qmark=qmark).skip_if(args.simple,default=True).ask():
        #Load the config.json.sample
        default_config = load_config(args.confdir,True)
        selected_teams = get_default_value(default_config,['preferences','teams'],"string")
        preferences_teams = []

        team_index=0
        team = None
        team = get_team(team_index,selected_teams,preferences_teams,qmark)
        preferences_teams.append(team)

        default_config['preferences']['teams'] = preferences_teams

        if questionary.confirm("Save {}/config.json file?".format(args.confdir),qmark=qmarksave,style=custom_style_dope).skip_if(args.simple,default=True).ask():
            save_config(default_config,args.confdir)
        sys.exit(0)
    else:
        #Do full setup or by sections?
        setup_type = questionary.select("What kind of setup do you want?",choices=['full','sections'],style=custom_style_dope,qmark=qmark).ask()


    nhl_config = default_config

    if setup_type == 'sections':
        sections  = (
            questionary.checkbox(
                "Select section(s) (no selection defaults to all sections)", choices=SECTIONS, style=custom_style_dope,qmark=qmark
            ).ask()
            or SECTIONS
        )
    else:
        sections = SECTIONS

    for section in sections:
        if section == "general":
            answers = general_settings(default_config,qmark)
            nhl_config.update(answers)

        if section == "preferences":
            preferences = preferences_settings(default_config,qmark)
            nhl_config.update(preferences)

        if section == "states":
            states = states_settings(default_config,qmark,setup_type)
            nhl_config.update(states)

        if section == "boards":
            boards_config = board_settings(default_config,qmark,setup_type)
            nhl_config['boards'] = boards_config

        if section == "sbio":
            sbio_config = sbio_settings(default_config,qmark,setup_type)
            nhl_config['sbio'] = sbio_config


    #Prepare to output to config.json file
    if questionary.confirm("Save {}/config.json file?".format(args.confdir),qmark=qmarksave,style=custom_style_dope).ask():
        save_config(nhl_config,args.confdir)

if __name__ == '__main__':
    main()
