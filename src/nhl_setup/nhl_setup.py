import questionary
from questionary import Validator, ValidationError, prompt
from styles import custom_style_dope

from print import *
import argparse
import functools
import regex
import json
import os
import sys
import shutil

from time import sleep


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
       


def get_file(path):
    dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(dir, path)

# Attempt to load a configuration file from config directory to use as defaults for prompts
# If config.json exists (user already created one, or this app has already been ran) user it,
# If no config.json exists, look for config.json.sample and if that doesn't exist, create a new config.json
def load_config(confdir):
    # Find and return a json file

        filename = ["config.json","config.json.sample"]
        j = {}
        jloaded = False
        fileindex = 0

        while not jloaded:

            if fileindex >= len(filename):
                jloaded = True
            else:
                path = get_file("{0}/{1}".format(confdir,filename[fileindex]))

            if os.path.isfile(path):
                j = json.load(open(path))
                jloaded = True
            else:
                fileindex += 1
                
        
        return j

def save_config(nhl_config,confdir):
    savefile = json.dumps(nhl_config, sort_keys=False, indent=4)
    #Make backup of original file if exists
    try:
        shutil.copyfile("{}/config.json".format(confdir),"{}/config.json.backup".format(confdir))
    except:
        print("Error making backup of {}/config.json".format(confdir),RED)

    with open('{}/config.json'.format(confdir),'w') as f:
        f.write(savefile)


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
    
    def_choices = ['Avalanche','Blackhawks','Blues','Blue Jackets','Bruins','Canadiens','Canucks','Capitals','Coyotes','Devils','Ducks','Flames','Flyers',
    'Golden Knights','Hurricanes','Islanders','Jets','Kings','Leafs','Lightning','Oilers','Panthers','Penguins','Predators',
    'Rangers','Red Wings','Sabres','Senators','Sharks','Stars','Wild']

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


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('confdir', nargs='?',default="config", type=str, help='Input dir for config.json')
    args = parser.parse_args()
    
    default_config = load_config(args.confdir)

    if questionary.confirm("Do you see a net,stick and horn?",style=custom_style_dope,qmark='🥅🏒🚨').ask():
        qmark = '🥅'
        qmarksave = '🥅🏒🚨'
    else:
        qmark = '?'
        qmarksave = '===>'

    questions = [

        {
            'type': 'confirm',
            'name': 'debug',
            'qmark': qmark,
            'message': 'Do you want debug on? (outputs log messages to console)',
            'default': get_default_value(default_config,['debug'],"bool")
        },
        {
            'type': 'confirm',
            'name': 'live_mode',
            'qmark': qmark,
            'message': 'Do you want live_mode on? (Shows live game data of favorite team)',
            'default': get_default_value(default_config,['live_mode'],"bool")
        }
    ]

    print("NHL LED SCOREBOARD SETUP", SMSLANT,RED, BOLD)
    nhl_config = {}

    answers = prompt(questions, style=custom_style_dope)

    nhl_config.update(answers)

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

    if len(selected_teams) > 0:
        selected_teams.remove(team)

    preferences_teams.append(team)
    team_select = select_teams(qmark)

    while team_select:
        team_index += 1
        team = get_team(team_index,selected_teams,preferences_teams,qmark)
        if team in selected_teams:
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

    nhl_config.update(preferences)

    goal_animations_dict ={'goal_animations':{}}

    questions = [

        {
            'type': 'confirm',
            'name': 'pref_team_only',
            'qmark': qmark,
            'message': 'Do you want goal animations for only preferred team?',
            'default': get_default_value(default_config,['goal_animations','pref_team_only'],"bool")
        },
    ]

    goal_animation_answer = prompt(questions,style=custom_style_dope)
    goal_animations_dict['goal_animations'].update(goal_animation_answer)

    nhl_config.update(goal_animations_dict)

    states = ['off_day','scheduled','intermission','post_game']
    state_index = 0
    temp_dict = {}

    while state_index < len(states):
        board_list = ['clock','scoreticker','standings','team_summary']
        
        boards_selected = []
        board = None
        select_board = True

        while select_board:
            board = get_board(states[state_index],board_list,qmark)
            boards_selected.append(board)
            board_list.remove(board)
            if len(board_list) != 0:
                select_board = select_boards(qmark)
            else:
                select_board=False
        
        temp_dict[states[state_index]] = boards_selected
        
        state_index+=1
        
    states_dict = {'states':{}}    
    states_dict['states'].update(temp_dict)
    nhl_config.update(states_dict)

    # Boards configuration
    boards_config = {'boards':{}}

    # Get scoreticker config

    scoreticker_questions = [
        {
            'type': 'confirm',
            'name': 'preferred_teams_only',
            'qmark': qmark,
            'message': 'Show preferred teams only? (Show only your preferred team or all games of the day)',
            'default': get_default_value(default_config,['boards','scoreticker','preferred_teams_only'],"bool")
        },
        {
            'type': 'input',
            'name': 'rotation_rate',
            'qmark': qmark,
            'message': 'Board rotation rate? (How often do you want to rotate the games shown)',
            'validate': lambda val: True if val.isdecimal() and int(val) >= 1 else 'Must be a number and greater or equal than 1',
            'filter': lambda val: int(val),
            'default': get_default_value(default_config,['boards','scoreticker','rotation_rate'],"int") or '5'
        }
    ]

    scoreticker_answers = prompt(scoreticker_questions,style=custom_style_dope)
    
    boards_config['boards']['scoreticker'] = scoreticker_answers

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

    standings_answers = prompt(standings_questions,style=custom_style_dope)

    boards_config['boards'].update(standings = standings_answers)

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
    ]

    clock_answers = prompt(clock_questions,style=custom_style_dope)

    boards_config['boards'].update(clock = clock_answers)
    
    nhl_config.update(boards_config)

    # SBIO configuration
    sbio_config = {'sbio':{'dimmer':{},'pushbutton':{}}}

    #Get default config
    sbio_default = get_default_value(default_config,['sbio'],"string")

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
    if use_dimmer['enabled'] or not sbio_default:
        sbio_config['sbio']['dimmer'].update(enabled = True)

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
        sbio_config['sbio']['dimmer'].update(dimmer_answers)
    else:
        sbio_default['dimmer'].update(enabled = False)
        sbio_config.update(sbio_default)

 
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
    if use_pb['enabled'] or not sbio_default:
        sbio_config['sbio']['pushbutton'].update(enabled = True)
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
                'validate': lambda val: True if val.isdecimal() and int(val) in [2,3,7,8,9,10,11,14,15,19,25] else 'Must be pin 2,3,7,8,9,10,11,14,15,19,25',
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
                'choices': ['clock','scoreticker','standings','team_summary'],
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
        sbio_config['sbio']['pushbutton'].update(pb_answers)
    else:
        sbio_default['pushbutton'].update(enabled = False)
        sbio_config.update(sbio_default)


    nhl_config.update(sbio_config)

    #Prepare to output to config.json file
    if questionary.confirm("Save {}/config.json file?".format(args.confdir),qmark=qmarksave,style=custom_style_dope).ask():
        save_config(nhl_config,args.confdir)

if __name__ == '__main__':
    main()
