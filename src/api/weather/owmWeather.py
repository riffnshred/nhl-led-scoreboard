from pyowm.owm import OWM
import debug
import geocoder
import datetime
from time import sleep
from api.weather.wx_utils import wind_chill, get_icons, degrees_to_direction, dew_point, wind_kmph, usaheatindex, temp_f

class owmWxWorker(object):
    def __init__(self, data, sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent
        self.weather_frequency = data.config.weather_update_freq
        self.time_format = data.config.time_format
        self.icons = get_icons("ecIcons_utf8.csv")
        self.apikey = data.config.weather_owm_apikey
        self.network_issues = False
        self.owm = OWM(self.apikey)
        self.owm_manager = self.owm.weather_manager()

    def run(self):

        if self.data.config.weather_units == "metric":
                self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]
        else:
                self.data.wx_units = ["F","mph","in","miles","MB","us"]

        while True:

            lat = self.data.latlng[0]
            lon = self.data.latlng[1]
            #Testing
            #lat = 32.653
            #lon = -83.7596
            try:
                debug.info("Refreshing OWM current observations weather")

                obs = self.owm_manager.weather_at_coords(lat,lon)
                self.network_issues = False
                self.data.wx_updated = True

            #except PyOWMError as e:
            #    #raise ValueError(e)
            #    debug.error("Unable to get OWM data error:{0}".format(e))
            #    self.data.wx_updated = False
            #    self.network_issues = True
            #    pass
            except Exception as e:
                debug.error("Unable to get OWM data error:{0}".format(e))
                self.data.wx_updated = False
                self.network_issues = True
                pass

            if not self.network_issues:
                wx = obs.weather.to_dict()
               
                if self.time_format == "%H:%M":
                    wx_timestamp = datetime.datetime.now().strftime("%m/%d %H:%M")
                else:
                    wx_timestamp = datetime.datetime.now().strftime("%m/%d %I:%M %p")

                owm_wxcode = int(wx.get("weather_code"))

                if owm_wxcode in range(200,299):
                    # Thunderstorm Class
                    owm_icon = 200
                elif owm_wxcode in range(300,399):
                    # Drizzle Class
                    owm_icon = 300
                elif owm_wxcode in range(500,599):
                    # Rain Class
                    owm_icon = 500
                elif owm_wxcode in range(600,699):
                    # Rain Class
                    owm_icon = 600
                elif owm_wxcode in range(801,804):
                    # Rain Class
                    owm_icon = 801
                else:
                    owm_icon = owm_wxcode
                
                

                #Get condition and icon from dictionary
                for row in range(len(self.icons)):
                    if int(self.icons[row]["OWMCode"]) == owm_icon:
                        wx_icon = self.icons[row]['font']
                        break
                    else:
                        wx_icon = '\uf07b' 
                
                wx_summary = wx.get("detailed_status")

                # Get wind information.  
                if self.data.config.weather_units != "metric":
                    wx_wind = obs.weather.wind(unit='miles_hour')
                else:
                    wx_wind = obs.weather.wind()

                owm_windspeed = wx_wind['speed']
                owm_windgust = wx_wind['gust']

                if self.data.config.weather_units == "metric":
                    # Convert m/s to km/h
                    owm_windspeed = wind_kmph(owm_windspeed)
                    owm_windgust = wind_kmph(owm_windgust)
                
                # Get icon and text wind direction
            
                owm_winddir = wx_wind.get("deg",0.0)
                winddir = degrees_to_direction(owm_winddir)
                
                wx_windgust = str(round(owm_windgust,1))+ self.data.wx_units[1] 
                wx_windspeed = str(round(owm_windspeed,1)) + self.data.wx_units[1]

                # Get temperature and apparent temperature based on weather units
                if self.data.config.weather_units == "metric":
                    owm_temp = obs.weather.temperature('celsius')['temp']
                    check_windchill = 10.0
                else:
                    owm_temp = obs.weather.temperature('fahrenheit')['temp']
                    check_windchill = 50.0
                
                if float(owm_temp) < check_windchill:
                    windchill = round(wind_chill(float(owm_temp),float(owm_windspeed),"mps"),1)
                    wx_app_temp = str(windchill) + self.data.wx_units[0]
                    wx_temp = str(round(owm_temp,1)) + self.data.wx_units[0]
                else:
                    if self.data.config.weather_units == "metric":
                        wx_app_temp = wx.get('humidity')
                    else:
                        wx_app_temp = wx.get('heat_index')
                        if wx_app_temp == None:
                            app_temp = usaheatindex(float(owm_temp),wx.get_humidity())
                            wx_app_temp = str(round(temp_f(app_temp),1)) + self.data.wx_units[0]

                    wx_temp = str(round(owm_temp,1)) + self.data.wx_units[0]

                wx_humidity = str(wx.get('humidity')) + "%"

                wx_dewpoint = str(round(dew_point(float(owm_temp),wx.get('humidity')),1))+ self.data.wx_units[0]

                wx_pressure = str(wx.get('pressure')['press']) + " " +self.data.wx_units[4]

                # Always set icon to N/A as owm doesn't return tendency for pressure

                wx_tendency = '\uf07b'

                vis_distance = wx.get('visibility_distance')
                if vis_distance == None:
                    vis_distance = 24100

                if self.data.config.weather_units == "metric":
                    owm_visibility = round(vis_distance/1000,1)
                    wx_visibility = str(owm_visibility) + " km"
                else:
                    owm_visibility = round(vis_distance*0.000621371,1)
                    wx_visibility = str(owm_visibility) + " mi"

                self.data.wx_current = [wx_timestamp,wx_icon,wx_summary,wx_temp ,wx_app_temp ,wx_humidity,wx_dewpoint]
                self.data.wx_curr_wind = [wx_windspeed,winddir[0],winddir[1],wx_windgust,wx_pressure,wx_tendency,wx_visibility]
                
            debug.info(self.data.wx_current)
            debug.info(self.data.wx_curr_wind)
            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)