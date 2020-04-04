from darksky.api import DarkSky
from darksky.types import languages, units, weather
from api.weather.wx_utils import degrees_to_direction
import debug
import datetime
from time import sleep

class dsWxWorker(object):
    def __init__(self, data, sleepEvent):
        self.data = data
        self.sleepEvent = sleepEvent
        self.weather_frequency = data.config.weather_update_freq
        self.apikey = data.config.weather_ds_apikey
        self.show_alerts = data.config.weather_show_alerts
        self.weather_alert = 0

        # DarkSky weather icons for top left of board using the weatherfont.ttf
        self.wx_cond = {"clear-day": '\uf00d',
                        "clear-night": '\uf02e',
                        "partly-cloudy-night": '\uf031',
                        "partly-cloudy-day": '\uf002',
                        "rain": '\uf019',
                        "snow": '\uf01b',
                        "sleet": '\uf0b5',
                        "wind": '\uf050',
                        "fog": '\uf014',
                        "cloudy": '\uf013',
                        "hail": '\uf015',
                        "thunderstorm": '\uf01e',
                        "tornado": '\uf056',
                        None: '\uf07b'
        }


    def run(self):# Synchronous way
        darksky = DarkSky(self.apikey)

        while True:
           
            forecast = darksky.get_forecast(
                self.data.latlng[0],self.data.latlng[1],
                extend=False, # default `False`
                lang=languages.ENGLISH, # default `ENGLISH`
                values_units=units.AUTO, # default `auto`
                exclude=[weather.MINUTELY,weather.HOURLY,weather.DAILY], # default `[]`,
                timezone=None # default None - will be set by DarkSky API automatically
            )
            
            self.data.wx_updated = True

            #Set up units [temp, wind speed,precip, storm distance]
            if forecast.flags.units in ["ca","si"]:
                self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]
            elif forecast.flags.units == "uk2":
                self.data.wx_units = ["C","mph","mm","miles","hPa","uk2"]
            else:
                self.data.wx_units = ["F","mph","in","miles","mbar","us"]
            
            if forecast.currently.wind_speed> 0:
                winddir = degrees_to_direction(forecast.currently.wind_bearing)
            else:
                winddir = degrees_to_direction(0)

            wx_windspeed = str(round(forecast.currently.wind_speed,1)) + " " + self.data.wx_units[1]
            wx_windgust = str(round(forecast.currently.wind_gust,1)) + " " + self.data.wx_units[1]
            wx_pressure = str(round(forecast.currently.pressure,1)) + " " + self.data.wx_units[4]

            self.data.wx_curr_wind = [wx_windspeed,winddir[0],winddir[1],wx_windgust,wx_pressure]
            
            wx_timestamp = forecast.currently.time.strftime("%m/%d %H:%M:%S")
            wx_temp = str(round(forecast.currently.temperature,1)) + self.data.wx_units[0]
            #wx_temp = str(round(forecast.currently.temperature,1))
            wx_app_temp = str(round(forecast.currently.apparent_temperature,1)) + self.data.wx_units[0]
            #wx_app_temp = str(round(forecast.currently.apparent_temperature,1))
            wx_humidity = str(round(100*forecast.currently.humidity,1)) + "%"

            self.data.wx_current = [wx_timestamp,self.wx_cond[forecast.currently.icon],forecast.currently.summary,wx_temp ,wx_app_temp ,wx_humidity]

            wx_precip_prob = str(round(forecast.currently.precip_probability,1)*100) + "%"
            self.data.wx_curr_precip = [forecast.currently.precip_type,wx_precip_prob,forecast.currently.precip_intensity,forecast.currently.precipAccumulation]

            if self.show_alerts and len(forecast.alerts) > 0:
                # Only get the latest alert
                i = -1

                # print(forecast.alerts[i].time)
                # print(forecast.alerts[i].expires)
                # print(forecast.alerts[i].title)
                # print(forecast.alerts[i].severity)
                # print(forecast.alerts[i].regions)

                wx_alert_time = forecast.alerts[-1].time.strftime("%m/%d %H:%M:%S")
                wx_alert_expires = forecast.alerts[-1].expires.strftime("%m/%d %H:%M:%S")
                #wx_storm_bearing = self.degrees_to_direction(forecast.currently.nearest_storm_bearing)
                #wx_storm_distance = str(forecast.currently.nearest_storm_distance) + " " + self.data.wx_units[3]
                self.data.wx_alerts = [forecast.alerts[-1].title,forecast.alerts[-1].severity,forecast.alerts[-1].regions,wx_alert_time,wx_alert_expires]
                debug.info(self.data.wx_alerts)
                self.weather_alert += 1
                self.sleepEvent.set()
                
            else:
                self.data.wx_alert_interrupt = False
                self.weather_alert = 0
                
            debug.info(self.data.wx_current)
            debug.info(self.data.wx_curr_wind)
            debug.info(self.data.wx_curr_precip)
            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)
