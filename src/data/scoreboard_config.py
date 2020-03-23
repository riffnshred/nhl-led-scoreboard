from utils import get_file
from data.layout import Layout
from data.colors import Color
from config.main import Config  
import json
import os
import sys
import debug

class ScoreboardConfig:
    def __init__(self, filename_base, args, size):
        json = self.__get_config(filename_base)

        # Misc config options
        self.debug = json["debug"]
        self.live_mode = json["live_mode"]

        # Preferences
        self.end_of_day = json["preferences"]["end_of_day"]
        self.time_format = self.__get_time_format(json["preferences"]["time_format"])

        self.live_game_refresh_rate = json["preferences"]["live_game_refresh_rate"]
        self.preferred_teams = json["preferences"]["teams"]
        self.sog_display_frequency = json["preferences"]["sog_display_frequency"]
        

        # Goal animation
        self.goal_anim_pref_team_only = json["goal_animations"]["pref_team_only"]

        # Dimmer preferences
        self.dimmer_enabled = json["sbio"]["dimmer"]["enabled"]
        self.dimmer_source = json["sbio"]["dimmer"]["source"]
        self.dimmer_frequency = json["sbio"]["dimmer"]["frequency"]
        self.dimmer_light_level_lux = json["sbio"]["dimmer"]["light_level_lux"]
        self.dimmer_mode = json["sbio"]["dimmer"]["mode"]
        self.dimmer_sunset_brightness = json["sbio"]["dimmer"]["sunset_brightness"]
        self.dimmer_sunrise_brightness = json["sbio"]["dimmer"]["sunrise_brightness"]

        # Pushbutton preferences
        self.pushbutton_enabled = json["sbio"]["pushbutton"]["enabled"]
        self.pushbutton_bonnet = json["sbio"]["pushbutton"]["bonnet"]
        self.pushbutton_pin = json["sbio"]["pushbutton"]["pin"]
        # Reboot duration should be a medium time press (ie greater than 2 seconds)
        self.pushbutton_reboot_duration = json["sbio"]["pushbutton"]["reboot_duration"]
        # Override process is used to trigger a different process other than the default.  reboot uses /sbin/reboot poweroff uses /sbin/poweroff
        self.pushbutton_reboot_override_process = json["sbio"]["pushbutton"]["reboot_override_process"]
        self.pushbutton_display_reboot = json["sbio"]["pushbutton"]["display_reboot"]
        # Poweroff duration should be a long press (greater than 5 or 6 seconds).  This is ties to the hold_time property of a button
        self.pushbutton_poweroff_duration = json["sbio"]["pushbutton"]["poweroff_duration"]
        self.pushbutton_poweroff_override_process = json["sbio"]["pushbutton"]["poweroff_override_process"]
        self.pushbutton_display_halt = json["sbio"]["pushbutton"]["display_halt"]
        self.pushbutton_state_triggered1 = json["sbio"]["pushbutton"]["state_triggered1"]
        self.pushbutton_state_triggered1_process = json["sbio"]["pushbutton"]["state_triggered1_process"]

        # Weather board preferences
        self.weather_enabled = json["weather"]["enabled"]
        self.weather_duration = json["weather"]["duration"]
        self.weather_ds_apikey = json["weather"]["ds_apikey"]
        self.weather_ds_iconset = json["weather"]["ds_iconset"]
        self.weather_update_freq = json["weather"]["update_freq"]
        #Allow the weather thread to interrupt the current flow of the display loop and show an alert if it shows up
        #Similar to how a pushbutton interrupts the flow
        self.weather_show_alerts = json["weather"]["show_alerts"] 

        # States
        '''TODO: Put condition so that the user dont leave any board list empty'''
        self.boards_off_day = json["states"]["off_day"]
        self.boards_scheduled = json["states"]["scheduled"]
        self.boards_intermission = json["states"]["intermission"]
        self.boards_post_game = json["states"]["post_game"]

        # Boards configuration
        # Boards
        # Scoreticker
        self.preferred_teams_only = json["boards"]["scoreticker"]["preferred_teams_only"]
        self.scoreticker_rotation_rate = json["boards"]["scoreticker"]["rotation_rate"]

        # Standings
        self.preferred_standings_only = json["boards"]["standings"]["preferred_standings_only"]
        self.standing_type = json["boards"]["standings"]["standing_type"]
        self.preferred_divisions = json["boards"]["standings"]["divisions"]
        self.preferred_conference = json["boards"]["standings"]["conference"]

        # Clock
        self.clock_board_duration = json["boards"]["clock"]["duration"]
        self.clock_hide_indicators = json["boards"]["clock"]["hide_indicator"]

        # Fonts
        self.layout = Layout()

        # load colors 
        self.team_colors = Color(self.__get_config(
            "colors/teams"
        ))

        self.config = Config(size)

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file("config/{}".format(filename))
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename, error=None):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)

        reference_config = self.read_json(filename)
        if not reference_config:
            if (error):
                debug.error(error)
            else:
                debug.error("Invalid {} config file. Make sure {} exists in config/".format(base_filename, base_filename))
            sys.exit(1)

        return reference_config

    def __get_time_format(self, config):
        # Set the time format to 12h.
        time_format = "%I:%M"

        # Check if the time format is different in the config. if so, change it.
        if config == "24h":
            time_format = "%H:%M"

        return time_format
