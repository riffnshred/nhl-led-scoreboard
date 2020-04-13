from noaa_sdk import noaa
import debug
import datetime
from time import sleep


class nwsWxAlerts(object):
    def __init__(self, data, sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent
        self.time_format = data.config.time_format
        self.weather_frequency = data.config.weather_update_freq
        self.weather_alert = 0
        # Date format Friday April 03, 2020 at 04:36 CDT
        self.alert_date_format = "%A %B %d, %Y at %H:%M %Z"
    
    def run(self):

        while True:
            
            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)