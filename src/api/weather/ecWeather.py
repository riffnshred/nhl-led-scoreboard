from env_canada import ECData
import debug
import geocoder
import datetime
from time import sleep
from api.weather.wx_utils import cadhumidex, wind_chill, get_icons, degrees_to_direction

class ecWxWorker(object):
    def __init__(self, data, sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent
        self.weather_frequency = data.config.weather_update_freq
        self.show_alerts = data.config.weather_show_alerts
        self.weather_alert = 0
        self.icons = get_icons("ecIcons_utf8.csv")
        # Date format Friday April 03, 2020 at 04:36 CDT
        self.alert_date_format = "%A %B %d, %Y at %H:%M %Z"
        

    def run(self):

        while True:
            ecData = ECData(coordinates=(self.data.latlng))
            #Set up units [temp, wind speed,precip, storm distance]
            #Use these eventhough some are included in data feed
            self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]

            curr_cond = ecData.conditions
            curr_alerts = ecData.alerts

            self.data.wx_updated = True

            wx_timestamp = datetime.datetime.now().strftime("%m/%d %H:%M:%S")

            #Check current temperature to determine if using windchill or heat for apparent temperature
            #Make sure we have a value.  Sometimes, the feed will not contain a value
            curr_temp = curr_cond.get("temperature").get("value",{})
            if curr_temp != None:
                curr_temp = float(curr_cond["temperature"]["value"])
                if curr_temp < 0:
                    windchill = round(wind_chill(float(curr_cond["temperature"]["value"]),float(curr_cond["wind_speed"]["value"]),self.data.wx_units[1]),1)
                    wx_app_temp = str(windchill) + self.data.wx_units[0]
                else:
                    humidex = round(cadhumidex(curr_temp,int(curr_cond["humidity"]["value"])),1)
                    wx_app_temp = str(humidex) + self.data.wx_units[0]
                wx_temp = curr_cond["temperature"]["value"] + self.data.wx_units[0]
            else:
                wx_temp = "N/A"
                wx_app_temp = "N/A"
            
            
            wx_humidity = curr_cond.get("humidity").get("value","N/A") + "%"

            #Get condition and icon from dictionary
            for row in range(len(self.icons)):
                if int(self.icons[row]["Code"]) == int(curr_cond.get("icon_code").get("value","90")):
                    wx_icon = self.icons[row]['font']
                    break
                else:
                    wx_icon = '\uf07b'
                
            wx_summary = curr_cond.get("condition").get("value","N/A")

            wx_dewpoint = curr_cond.get("dewpoint").get("value","N/A") + self.data.wx_units[0]

            self.data.wx_current = [wx_timestamp,wx_icon,wx_summary,wx_temp ,wx_app_temp ,wx_humidity,wx_dewpoint]


            winddir = degrees_to_direction(float(curr_cond.get("wind_bearing").get("value","0")))
            wx_windspeed = str(round(float(curr_cond.get("wind_speed").get("value","0.0")),1)) + " " + self.data.wx_units[1]
            
            wx_windgust = str(round(float(curr_cond.get("wind_gust").get("value","0.0")),1)) + " " + self.data.wx_units[1]

            wx_pressure = str(round(float(curr_cond.get("pressure").get("value","0")),1) * 10) + " " + self.data.wx_units[4]

            for row in range(len(self.icons)):
                if self.icons[row]["Description"].lower() == curr_cond.get("tendency").get("value","N/A"):
                    wx_tendency = self.icons[row]['font']
                    break
                else:
                    wx_tendency = '\uf07b'
            
            wx_visibility = curr_cond.get("visibility").get("value","24") + " " + curr_cond.get("visibility").get("unit","km")

            self.data.wx_curr_wind = [wx_windspeed,winddir[0],winddir[1],wx_windgust,wx_pressure,wx_tendency,wx_visibility]

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

            debug.info(self.data.wx_current)
            debug.info(self.data.wx_curr_wind)

            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)

