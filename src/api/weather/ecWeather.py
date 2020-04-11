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
        self.time_format = data.config.time_format
        self.weather_alert = 0
        self.icons = get_icons("ecIcons_utf8.csv")
        
        

    def run(self):

        while True:
            ecData = ECData(coordinates=(self.data.latlng))
            #Set up units [temp, wind speed,precip, storm distance]
            #Use these eventhough some are included in data feed
            self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]

            curr_cond = ecData.conditions
            #curr_alerts = ecData.alerts

            self.data.wx_updated = True

            if self.time_format == "%H:%M":
                wx_timestamp = datetime.datetime.now().strftime("%m/%d %H:%M")
            else:
                wx_timestamp = datetime.datetime.now().strftime("%m/%d %I:%M %p")

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
            if curr_cond.get("wind_gust").get("value","0.0") != None:
                wx_windgust = str(round(float(curr_cond.get("wind_gust").get("value","0.0")),1)) + " " + self.data.wx_units[1]
            else:
                wx_windgust = "0.0 " + self.data.wx_units[1]

            wx_pressure = str(round(float(curr_cond.get("pressure").get("value","0")),1) * 10) + " " + self.data.wx_units[4]

            for row in range(len(self.icons)):
                if self.icons[row]["Description"].lower() == curr_cond.get("tendency").get("value","N/A"):
                    wx_tendency = self.icons[row]['font']
                    break
                else:
                    wx_tendency = '\uf07b'
            
            wx_visibility = curr_cond.get("visibility").get("value","24") + " " + curr_cond.get("visibility").get("unit","km")

            self.data.wx_curr_wind = [wx_windspeed,winddir[0],winddir[1],wx_windgust,wx_pressure,wx_tendency,wx_visibility]


            debug.info(self.data.wx_current)
            debug.info(self.data.wx_curr_wind)

            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)

