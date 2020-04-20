from env_canada import ECData
import debug
import datetime
from time import sleep
from api.weather.wx_utils import cadhumidex, wind_chill, get_icons, degrees_to_direction, temp_f, wind_mph

class ecWxWorker(object):
    def __init__(self, data, sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent
        self.weather_frequency = data.config.weather_update_freq
        self.time_format = data.config.time_format
        self.icons = get_icons("ecIcons_utf8.csv")
        
        

    def run(self):

        while True:
            try:
                ecData = ECData(coordinates=(self.data.latlng))
            except requests.exceptions.RequestException as e:
                raise ValueError(e)
                debug.error("Unable to get EC data")
                pass

            #Set up units [temp, wind speed,precip, storm distance]
            #Use these eventhough some are included in data feed
            if self.data.config.weather_units == "metric":
                self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]
            else:
                self.data.wx_units = ["F","mph","in","miles","MB","us"]

            curr_cond = ecData.conditions

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
                check_windchill = 10.0
                if self.data.config.weather_units == "imperial":
                    curr_temp = temp_f(curr_temp)
                    check_windchill = 50.0


                if curr_temp < check_windchill:
                    windchill = round(wind_chill(float(curr_cond["temperature"]["value"]),float(curr_cond["wind_speed"]["value"]),self.data.wx_units[1]),1)
                    wx_app_temp = str(windchill) + self.data.wx_units[0]
                else:
                    humidex = round(cadhumidex(curr_temp,int(curr_cond["humidity"]["value"])),1)
                    wx_app_temp = str(humidex) + self.data.wx_units[0]
                wx_temp = str(round(curr_temp,1)) + self.data.wx_units[0]

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

            curr_dewpoint = float(curr_cond.get("dewpoint").get("value","0.0"))

            if self.data.config.weather_units == "imperial":
                curr_dewpoint = round(temp_f(curr_dewpoint),1)

            wx_dewpoint = str(curr_dewpoint) + self.data.wx_units[0]

            self.data.wx_current = [wx_timestamp,wx_icon,wx_summary,wx_temp ,wx_app_temp ,wx_humidity,wx_dewpoint]


            winddir = degrees_to_direction(float(curr_cond.get("wind_bearing").get("value","0")))

            curr_windspeed = float(curr_cond.get("wind_speed").get("value","0.0"))
            
            if self.data.config.weather_units == "imperial":
                curr_windspeed = round(wind_mph(curr_windspeed),1)

            wx_windspeed = str(curr_windspeed) + " " + self.data.wx_units[1]
             
            if curr_cond.get("wind_gust").get("value","0.0") != None:
                curr_windgust = float(curr_cond.get("wind_gust").get("value","0.0"))
                if self.data.config.weather_units == "imperial":
                    curr_windgust = round(wind_mph(curr_windgust),1)

                wx_windgust = str(curr_windgust) + " " + self.data.wx_units[1]
            else:
                wx_windgust = "0.0 " + self.data.wx_units[1]

            wx_pressure = str(round(float(curr_cond.get("pressure").get("value","0")),1) * 10) + " " + self.data.wx_units[4]

            for row in range(len(self.icons)):
                if self.icons[row]["Description"].lower() == curr_cond.get("tendency").get("value","N/A"):
                    wx_tendency = self.icons[row]['font']
                    break
                else:
                    wx_tendency = '\uf07b'
            
            if self.data.config.weather_units == "imperial":
                imp_visibility = round(float(curr_cond.get("visibility").get("value","24"))*0.621371,1)
                wx_visibility = str(imp_visibility) + " mi"
            else:
                wx_visibility = curr_cond.get("visibility").get("value","24") + " " + curr_cond.get("visibility").get("unit","km")


            self.data.wx_curr_wind = [wx_windspeed,winddir[0],winddir[1],wx_windgust,wx_pressure,wx_tendency,wx_visibility]


            debug.info(self.data.wx_current)
            debug.info(self.data.wx_curr_wind)

            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)

