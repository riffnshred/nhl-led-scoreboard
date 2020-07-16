import questionary
from questionary import Validator, ValidationError, prompt
from styles import custom_style_dope
from validate_json import validateConf
from print import *
import argparse
import functools
import regex
import json
import os
import sys
import shutil


from time import sleep

SCRIPT_VERSION = "1.3.0 - Wx version"

TEAMS = ['Avalanche','Blackhawks','Blues','Blue Jackets','Bruins','Canadiens','Canucks','Capitals','Coyotes','Devils','Ducks','Flames','Flyers',
    'Golden Knights','Hurricanes','Islanders','Jets','Kings','Maple Leafs','Lightning','Oilers','Panthers','Penguins','Predators',
    'Rangers','Red Wings','Sabres','Senators','Sharks','Stars','Wild']

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
# If config.json exists (user already created one, or this app has already been ran) use it,
# If no config.json exists, look for config.json.sample and if that doesn't exist, create a new config.json
# If simple = True, force the config file to be the config.json.sample as we are setting up with defaults

def load_config(confdir,simple=False):
    # Find and return a json file

        filename = ["config.json","config.json.sample"]
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
                    sys.exit(0)
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
        sys.exit(0)
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

def select_us_states(qmark):
    us_state_select_answer = [
        {
            'type': 'confirm',
            'name': 'us_state_select',
            'qmark': qmark,
            'message': 'Add another US State?',
            'default': True
        }
    ]
    answer = prompt(us_state_select_answer)
    
    return answer['us_state_select']

def select_countries(qmark):
    country_select_answer = [
        {
            'type': 'confirm',
            'name': 'country_select',
            'qmark': qmark,
            'message': 'Add another Country?',
            'default': True
        }
    ]
    answer = prompt(country_select_answer)
    
    return answer['country_select']

def select_canada_prov(qmark):
    canada_prov_select_answer = [
        {
            'type': 'confirm',
            'name': 'canada_prov_select',
            'qmark': qmark,
            'message': 'Add another Province?',
            'default': True
        }
    ]
    answer = prompt(canada_prov_select_answer)
    
    return answer['canada_prov_select']


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

def get_us_states(us_state_index,us_state_choices,pref_us_states,qmark):
    
    def_choices = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District Of Columbia','Florida','Georgia','Guam',
    'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
    'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota',
    'Northern Mariana Islands','Ohio','Oklahoma','Oregon','Pennsylvania','Puerto Rico','Rhode Island','South Carolina','South Dakota','Tennessee',
    'Texas','United States Virgin Islands','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

    choices = []

    if len(pref_us_states) >= 0 and len(us_state_choices) > 0:
        #Combine lists with US States from us_state_choices first
        choices = [ele for ele in def_choices if ele not in us_state_choices]
        if len(pref_us_states) > 0:
            choices = [ele for ele in def_choices if ele not in pref_us_states]
        choices = us_state_choices + choices
    
    if len(pref_us_states) > 0 and len(us_state_choices) == 0:
        # Remove anything all ready selected from the choices list
        choices = [ele for ele in def_choices if ele not in pref_us_states]

    if len(pref_us_states) == 0 and len(us_state_choices) == 0:
        choices = def_choices

    if us_state_index == 0:
        message = "Select your covid19 states:"
    else:
        message = "Select a US State for Covid19 board"

    us_state_prompt = [
        {
            'type': 'list',
            'name': 'us_state',
            'qmark': qmark,
            'message': message,
            'choices': choices,
        }
    ]
    answers = prompt(us_state_prompt,style=custom_style_dope)
    return answers['us_state']

def get_countries(country_index,country_choices,pref_countries,qmark):
    
    def_choices = ['USA','Canada','China','Iran','Italy','France','Afghanistan','Albania','Algeria','Andorra','Angola','Anguilla','Antigua and Barbuda','Argentina','Armenia','Aruba','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bermuda','Bhutan','Bolivia','Bosnia and Herzegovina','Botswana','Brazil',
    'British Virgin Islands','Brunei','Bulgaria','Burkina Faso','CAR','Cabo Verde','Cambodia','Cameroon','Cayman Islands','Chad','Channel Islands','Chile','Colombia','Congo','Costa Rica','Croatia','Cuba','Curaçao','Cyprus','Czechia','DRC','Denmark','Diamond Princess','Djibouti','Dominica','Dominican Republic','Ecuador','Egypt','El Salvador','Equatorial Guinea',
    'Eritrea','Estonia','Eswatini','Ethiopia','Faeroe Islands','Fiji','Finland','French Guiana','French Polynesia','Gabon','Gambia','Georgia','Germany','Ghana','Gibraltar','Greece','Greenland','Grenada','Guadeloupe','Guatemala','Guinea','Guinea-Bissau','Guyana','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iraq','Ireland','Isle of Man',
    'Israel','Ivory Coast','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','MS Zaandam','Macao','Madagascar','Malaysia','Maldives','Mali','Malta','Martinique','Mauritania','Mauritius','Mayotte','Mexico','Moldova','Monaco','Mongolia','Montenegro','Montserrat',
    'Morocco','Mozambique','Myanmar','Namibia','Nepal','Netherlands','New Caledonia','New Zealand','Nicaragua','Niger','Nigeria','North Macedonia','Norway','Oman','Pakistan','Palestine','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Qatar','Romania','Russia','Rwanda','Réunion','S. Korea','Saint Kitts and Nevis','Saint Lucia','Saint Martin',
    'San Marino','Saudi Arabia','Senegal','Serbia','Seychelles','Singapore','Sint Maarten','Slovakia','Slovenia','Somalia','South Africa','Spain','Sri Lanka','St. Barth','St. Vincent Grenadines','Sudan','Suriname','Sweden','Switzerland','Syria','Taiwan','Tanzania','Thailand','Timor-Leste','Togo','Trinidad and Tobago','Tunisia','Turkey','Turks and Caicos','UAE','UK','Uganda',
    'Ukraine','Uruguay','Uzbekistan','Vatican City','Venezuela','Vietnam','Zambia','Zimbabwe']

    choices = []

    if len(pref_countries) >= 0 and len(country_choices) > 0:
        #Combine lists with countries from country_choices first
        choices = [ele for ele in def_choices if ele not in country_choices]
        if len(pref_countries) > 0:
            choices = [ele for ele in def_choices if ele not in pref_countries]
        choices = country_choices + choices
    
    if len(pref_countries) > 0 and len(country_choices) == 0:
        # Remove anything all ready selected from the choices list
        choices = [ele for ele in def_choices if ele not in pref_countries]

    if len(pref_countries) == 0 and len(country_choices) == 0:
        choices = def_choices

    if country_index == 0:
        message = "Select your covid19 countries:"
    else:
        message = "Select a country for covid19 board"

    country_prompt = [
        {
            'type': 'list',
            'name': 'country',
            'qmark': qmark,
            'message': message,
            'choices': choices,
        }
    ]
    answers = prompt(country_prompt,style=custom_style_dope)
    return answers['country']

def get_canada_prov(canada_prov_index,canada_prov_choices,pref_canada_prov,qmark):
    
    def_choices = ['Alberta','British Columbia','Manitoba','New Brunswick','Newfoundland and Labrador','Northwest Territories','Nova Scotia','Ontario','Prince Edward Island','Quebec','Saskatchewan','Yukon']

    choices = []

    if len(pref_canada_prov) >= 0 and len(canada_prov_choices) > 0:
        #Combine lists with Canada provinces from canada_prov_choices first
        choices = [ele for ele in def_choices if ele not in canada_prov_choices]
        if len(pref_canada_prov) > 0:
            choices = [ele for ele in def_choices if ele not in pref_canada_prov]
        choices = canada_prov_choices + choices
    
    if len(pref_canada_prov) > 0 and len(canada_prov_choices) == 0:
        # Remove anything all ready selected from the choices list
        choices = [ele for ele in def_choices if ele not in pref_canada_prov]

    if len(pref_canada_prov) == 0 and len(canada_prov_choices) == 0:
        choices = def_choices

    if canada_prov_index == 0:
        message = "Select your covid19 Canadian provinces:"
    else:
        message = "Select a Canadian province for Covid19 board"

    canada_prov_prompt = [
        {
            'type': 'list',
            'name': 'canada_prov',
            'qmark': qmark,
            'message': message,
            'choices': choices,
        }
    ]
    answers = prompt(canada_prov_prompt,style=custom_style_dope)
    return answers['canada_prov']

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('confdir', nargs='?',default="config", type=str, help='Input dir for config.json (defaults to config)')
    parser.add_argument('--version','-v', action='version', version='%(prog)s ' + SCRIPT_VERSION)
    parser.add_argument('--team','-t',nargs=1, action='store',type=str,help="Create simple config.json with defaults and one team")
    parser.add_argument('--check','-c',action='store_true',help="Check config.json against schema, used to see if config is out of date")
    args = parser.parse_args()
    
    print("NHL LED SCOREBOARD SETUP", SMSLANT,RED, BOLD)
    print(SCRIPT_VERSION,UNDERLINE,BLUE)

    if not os.path.exists(args.confdir):
        # Get current working directory
        setup_cwd = os.getcwd()
        print("Directory {0}/{1} does not exist.  Are you running in the right directory?".format(setup_cwd,args.confdir),RED)
        sys.exit(0)

    #Check to see if the user wants to validate an existing config.json against the schema
    #Only from command line

    if args.check:
        conffile = "{0}/config.json".format(args.confdir)
        schemafile = "{0}/config.schema.json".format(args.confdir)

        confpath = get_file(conffile)
        schemapath = get_file(schemafile)
        print("Now validating config......")
        (valid,msg) = validateConf(confpath,schemapath)
        if valid:
            print("Your config.json passes validation and can be used with nhl led scoreboard",GREEN)
        else:
            print("Your config.json fails validation: error: [{0}]".format(msg),RED)
        sys.exit(0)

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
        sys.exit(0)
    else:
        default_config = load_config(args.confdir)



    if questionary.confirm("Do you see a net,stick and horn?",style=custom_style_dope,qmark='🥅🏒🚨').ask():
        qmark = '🥅'
        qmarksave = '🥅🏒🚨'
    else:
        qmark = '?'
        qmarksave = '===>'

    if questionary.confirm("Do you want a simple default setup with one team selection (Y) or full setup (N)?",style=custom_style_dope,qmark=qmark).ask():
        #Load the config.json.sample
        default_config = load_config(args.confdir,True)
        selected_teams = get_default_value(default_config,['preferences','teams'],"string")
        preferences_teams = []

        team_index=0
        team = None
        team = get_team(team_index,selected_teams,preferences_teams,qmark)
        preferences_teams.append(team)
        
        default_config['preferences']['teams'] = preferences_teams
        
        if questionary.confirm("Save {}/config.json file?".format(args.confdir),qmark=qmarksave,style=custom_style_dope).ask():
            save_config(default_config,args.confdir)
        sys.exit(0)

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

    location = [
        {
            'type': 'input',
            'name': 'location',
            'qmark': qmark,
            'message': 'Your location to override latitude and longitude lookup via IP (City, State or City, Province)',
            'default': get_default_value(default_config,['preferences','location'],"string") or 'Winnipeg, MB'
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
        board_list = ['clock','weather','scoreticker','standings','team_summary','covid_19']
        
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
    
    # COVID board questions
    # COVID Worldwide Enabled Question
    covid_ww_question = [
        {
            'type': 'confirm',
            'name': 'worldwide_enabled',
            'qmark': qmark,
            'message': 'Enable Covid board for World Wide data?',
            'default': get_default_value(default_config,['boards','covid19','worldwide_enabled'],"bool")
        }
    ]
    covid_ww_answer = prompt(covid_ww_question,style=custom_style_dope)
    boards_config['boards'].update(covid19 = covid_ww_answer)
    
    # COVID Country Enabled Question
    covid_country_question = [
        {
            'type': 'confirm',
            'name': 'country_enabled',
            'qmark': qmark,
            'message': 'Enable Covid board for specific Countries?',
            'default': get_default_value(default_config,['boards','covid19','country_enabled'],"bool")
        }
    ]
    covid_country_answer = prompt(covid_country_question,style=custom_style_dope)
    boards_config['boards']['covid19'].update(covid_country_answer)
    
    # COVID country configuration
    selected_countries = get_default_value(default_config,['boards','covid19','country'],"string")
    if covid_country_answer['country_enabled']:
        
        preferences_countries = []

        country_index=0
        country = None
        country = get_countries(country_index,selected_countries,preferences_countries,qmark)

        if len(selected_countries) > 0 and (country in selected_countries):
            selected_countries.remove(country)

        preferences_countries.append(country)
        country_select = select_countries(qmark)

        while country_select:
            country_index += 1
            country = get_countries(country_index,selected_countries,preferences_countries,qmark)
            if len(selected_countries) > 0 and (country in selected_countries):
                selected_countries.remove(country)
            preferences_countries.append(country)
            country_select = select_countries(qmark)

        preferences_country_dict = {'country':preferences_countries}
        boards_config['boards']['covid19'].update(preferences_country_dict)
    else:
        preferences_country_dict = {'country':selected_countries}
        boards_config['boards']['covid19'].update(preferences_country_dict)

    # COVID US State Enabled question
    covid_us_state_question = [
        {
            'type': 'confirm',
            'name': 'us_state_enabled',
            'qmark': qmark,
            'message': 'Enable Covid board for specific US states?',
            'default': get_default_value(default_config,['boards','covid19','us_state_enabled'],"bool")
        }
    ]
    covid_us_state_answer = prompt(covid_us_state_question,style=custom_style_dope)
    boards_config['boards']['covid19'].update(covid_us_state_answer)
    
    # COVID US State configuration
    selected_us_states = get_default_value(default_config,['boards','covid19','us_state'],"string")
    if covid_us_state_answer['us_state_enabled']:
        preferences_us_states = []

        us_state_index=0
        us_state = None
        us_state = get_us_states(us_state_index,selected_us_states,preferences_us_states,qmark)

        if len(selected_us_states) > 0 and (us_state in selected_us_states):
            selected_us_states.remove(us_state)

        preferences_us_states.append(us_state)
        us_state_select = select_us_states(qmark)

        while us_state_select:
            us_state_index += 1
            us_state = get_us_states(us_state_index,selected_us_states,preferences_us_states,qmark)
            if len(selected_us_states) > 0 and (us_state in selected_us_states):
                selected_us_states.remove(us_state)
            preferences_us_states.append(us_state)
            us_state_select = select_us_states(qmark)

        preferences_us_state_dict = {'us_state':preferences_us_states}
        boards_config['boards']['covid19'].update(preferences_us_state_dict)
    else:
        preferences_us_state_dict = {'us_state':selected_us_states}
        boards_config['boards']['covid19'].update(preferences_us_state_dict)
    # COVID Canadian province enabled question
    covid_canada_prov_question = [
        {
            'type': 'confirm',
            'name': 'canada_enabled',
            'qmark': qmark,
            'message': 'Enable Covid board for specific Canadian provinces?',
            'default': get_default_value(default_config,['boards','covid19','canada_enabled'],"bool")
        }
    ]
    covid_canada_answer = prompt(covid_canada_prov_question,style=custom_style_dope)
    boards_config['boards']['covid19'].update(covid_canada_answer)
    
    # COVID Canadian province configuration
    selected_canada_prov = get_default_value(default_config,['boards','covid19','canada_prov'],"string")
    if covid_canada_answer['canada_enabled']:
        
        preferences_canada_prov = []

        canada_prov_index=0
        canada_prov = None
        canada_prov = get_canada_prov(canada_prov_index,selected_canada_prov,preferences_canada_prov,qmark)

        if len(selected_canada_prov) > 0 and (canada_prov in selected_canada_prov):
            selected_canada_prov.remove(canada_prov)

        preferences_canada_prov.append(canada_prov)
        canada_prov_select = select_canada_prov(qmark)

        while canada_prov_select:
            canada_prov_index += 1
            canada_prov = get_canada_prov(canada_prov_index,selected_canada_prov,preferences_canada_prov,qmark)
            if len(selected_canada_prov) > 0 and (canada_prov in selected_canada_prov):
                selected_canada_prov.remove(canada_prov)
            preferences_canada_prov.append(canada_prov)
            canada_prov_select = select_canada_prov(qmark)

        preferences_canada_prov_dict = {'canada_prov':preferences_canada_prov}
        boards_config['boards']['covid19'].update(preferences_canada_prov_dict)
    else:
        preferences_canada_prov_dict = {'canada_prov':selected_canada_prov}
        boards_config['boards']['covid19'].update(preferences_canada_prov_dict)

    #Add weather info
    #Get default config
    wx_default = get_default_value(default_config,['boards','weather'],"string")

    wx_enabled = [
        {
            'type': 'confirm',
            'name': 'enabled',
            'qmark': qmark,
            'message': 'Use weather board?',
            'default': get_default_value(default_config,['boards','weather','enabled'],"bool") or True
        }
    ]

    use_wx = prompt(wx_enabled,style=custom_style_dope)

    boards_config['boards'].update(weather = use_wx)

    if use_wx['enabled']:

        wx_questions = [

            {
                'type': 'input',
                'name': 'units',
                'qmark': qmark,
                'message': 'Units to display? (mertic or imperial)',
                'default': get_default_value(default_config,['boards','weather','units'],"string") or "metric"
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
                'type': 'input',
                'name': 'data_feed',
                'qmark': qmark,
                'message': 'Which weather data feed for current observations? (EC or OWM)\nEC=Environment Canada\nOWM=Open Weather Map (requires a key: works for all locations)',
                'default': get_default_value(default_config,['boards','weather','data_feed'],"string") or 'EC'
            },
            {
                'type': 'input',
                'name': 'alert_feed',
                'qmark': qmark,
                'message': 'Which weather feed for alerts? (EC or NWS)\nEC=Environment Canada\nNWS=National Weather Service (US only)',
                'default': get_default_value(default_config,['boards','weather','alert_feed'],"string") or 'EC'
            },
            {
                'type': 'input',
                'name': 'owm_apikey',
                'qmark': qmark,
                'message': 'OpenWeatherMap API key if using OWM as data feed: (get key from https://openweathermap.org/appid)',
                'default': get_default_value(default_config,['boards','weather','owm_apikey'],"string") or ''
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
            'type': 'confirm',
            'name': 'show_alerts',
            'qmark': qmark,
            'message': 'Show weather alerts?',
            'default': get_default_value(default_config,['boards','weather','show_alerts'],"bool") or True
            },
            {
            'type': 'confirm',
            'name': 'alert_title',
            'qmark': qmark,
            'message': 'On alert board, display title of alert (warning, watch, advisory)?',
            'default': get_default_value(default_config,['boards','weather','alert_title'],"bool") or True
            },
            {
            'type': 'confirm',
            'name': 'scroll_alert',
            'qmark': qmark,
            'message': 'On alert board, scroll alert?',
            'default': get_default_value(default_config,['boards','weather','scroll_alert'],"bool") or True
            },
            {
                'type': 'input',
                'name': 'alert_duration',
                'qmark': qmark,
                'validate': lambda val: True if val.isdecimal() and int(val) >= 5 else 'Must be a number and greater or equal than 5',
                'filter': lambda val: int(val),
                'message': 'How long (in seconds) to show the alert board',
                'default': get_default_value(default_config,['boards','weather','alert_duration'],"int") or '5'
            },
            {
            'type': 'confirm',
            'name': 'show_on_clock',
            'qmark': qmark,
            'message': 'Display temperature and humidity on clock?',
            'default': get_default_value(default_config,['boards','weather','show_on_clock'],"bool") or True
            },
        ]
        
        wx_answers = prompt(wx_questions,style=custom_style_dope)
        boards_config['boards']['weather'].update(wx_answers)
    else:
        boards_config['boards']['weather'].update(wx_default)

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
        sbio_config['sbio']['dimmer'].update(enabled = False)
        sbio_config['sbio'].update(sbio_default)


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
                'choices': ['clock','weather','scoreticker','standings','team_summary','covid_19'],
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
        sbio_config['sbio']['pushbutton'].update(enabled = False)
        sbio_config['sbio'].update(sbio_default)


    nhl_config.update(sbio_config)


    #Prepare to output to config.json file
    if questionary.confirm("Save {}/config.json file?".format(args.confdir),qmark=qmarksave,style=custom_style_dope).ask():
        save_config(nhl_config,args.confdir)

if __name__ == '__main__':
    main()
    