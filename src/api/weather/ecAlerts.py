from env_canada import ECData
import debug
import geocoder
import datetime
from time import sleep


def ecWxAlerts(object):
    def __init__(self, data, sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent

        self.weather_frequency = data.config.weather_update_freq
        self.show_alerts = data.config.weather_show_alerts
        self.weather_alert = 0

    def run(self):

        while True:
            ecData = ECData(coordinates=(self.data.latlng))
            curr_alerts = ecData.alerts
            
            if self.show_alerts and len(curr_alerts) > 0:
                # Only get the latest alert
                i = -1

                # Create the warnings, watches and advisory lists from curr_alerts but only take the most recent one

                wx_num_endings = len(curr_alerts.get("endings").get("value","0"))
                wx_num_warning = len(curr_alerts.get("warnings").get("value","0"))
                wx_num_watch = len(curr_alerts.get("watches").get("value","0"))
                wx_num_advisory = len(curr_alerts.get("advisories").get("value","0"))
                
                if wx_num_warning > 0:
                    warn_date = curr_alerts["warnings"]["value"][i]["date"]
                    #Convert to date for display
                    warn_datetime = datetime.datetime.strptime(warn_date,self.alert_date_format)
                    wx_alert_time = warn_datetime.strftime("%m/%d %H:%M")
                    self.data.wx_alerts = [curr_alerts["warnings"]["value"][i]["title"],"warning",wx_alert_time]
                elif wx_num_watch > 0:
                    watch_date = curr_alerts["watches"]["value"][i]["date"]
                    #Convert to date for display
                    watch_datetime = datetime.datetime.strptime(watch_date,self.alert_date_format)
                    wx_alert_time = watch_datetime.strftime("%m/%d %H:%M")
                    self.data.wx_alerts = [curr_alerts["watches"]["value"][i]["title"],"watch",wx_alert_time]
                elif wx_num_advisory > 0:
                    advisory_date = curr_alerts["watches"]["value"][i]["date"]
                    #Convert to date for display
                    advisory_datetime = datetime.datetime.strptime(advisory_date,self.alert_date_format)
                    wx_alert_time = advisory_datetime.strftime("%m/%d %H:%M")
                    self.data.wx_alerts = [curr_alerts["advisories"]["value"][i]["title"],"advisory",wx_alert_time]
                elif wx_num_endings > 0:
                    ending_date = curr_alerts["endings"]["value"][i]["date"]
                    #Convert to date for display
                    ending_datetime = datetime.datetime.strptime(ending_date,self.alert_date_format)
                    wx_alert_time = ending_datetime.strftime("%m/%d %H:%M")
                    self.data.wx_alerts = [curr_alerts["endings"]["value"][i]["title"],"ended",wx_alert_time]
                    self.data.wx_alert_interrupt = False
                    self.weather_alert = 0
                else:
                    self.data.wx_alert_interrupt = False
                    self.weather_alert = 0

                if len(self.data.wx_alerts) > 0:
                    debug.info(self.data.wx_alerts)

                if wx_num_endings == 0:
                    self.weather_alert += 1
                    self.sleepEvent.set()
                
            else:
                self.data.wx_alert_interrupt = False
                self.weather_alert = 0