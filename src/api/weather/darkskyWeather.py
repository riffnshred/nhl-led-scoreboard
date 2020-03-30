from darksky.api import DarkSky
from darksky.types import languages, units, weather
import debug
import geocoder
import datetime
from time import sleep

class weatherWorker(object):
    def __init__(self, data, sleepEvent):
        g = geocoder.ip('me')
        debug.info("location for weather is: " + g.city + ","+ g.country + " " + str(g.latlng))
        self.lat = g.lat
        self.lng = g.lng
        self.data = data
        self.sleepEvent = sleepEvent
        self.weather_frequency = data.config.weather_update_freq
        self.apikey = data.config.weather_ds_apikey
        self.show_alerts = data.config.weather_show_alerts
        self.weather_alert = 0


    def degrees_to_direction(self, degrees):
        try:
            degrees = float(degrees)
        except ValueError:
            return [None,"\uf07b"]

        if degrees < 0 or degrees > 360:
            return [None,"\uf07b"]

        if degrees <= 11.25 or degrees >= 348.76:
            return ["N","\uf060"]
        elif degrees <= 33.75:
            return ["NNE","\uf05e"]
        elif degrees <= 56.25:
            return ["NE","\uf05e"]
        elif degrees <= 78.75:
            return ["ENE","\uf05e"]
        elif degrees <= 101.25:
            return ["E","\uf061"]
        elif degrees <= 123.75:
            return ["ESE","\uf05b"]
        elif degrees <= 146.25:
            return ["SE","\uf05b"]
        elif degrees <= 168.75:
            return ["SSE","\uf05b"]
        elif degrees <= 191.25:
            return ["S","\uf05c"]
        elif degrees <= 213.75:
            return ["SSW","\uf05a"]
        elif degrees <= 236.25:
            return ["SW","\uf05a"]
        elif degrees <= 258.75:
            return ["WSW","\uf05a"]
        elif degrees <= 281.25:
            return ["W","\uf059"]
        elif degrees <= 303.75:
            return ["WNW","\uf05d"]
        elif degrees <= 326.25:
            return ["NW","\uf05d"]
        elif degrees <= 348.75:
            return ["NNW","\uf05d"]
        else:
            return [None,"\uf07b"]

    def run(self):# Synchronous way
        darksky = DarkSky(self.apikey)

        while True:
           # lat = 36.229
           # lng = -93.107
           # Get the current forecast and any alerts
            forecast = darksky.get_forecast(
                self.lat, self.lng,
                extend=False, # default `False`
                lang=languages.ENGLISH, # default `ENGLISH`
                values_units=units.AUTO, # default `auto`
                exclude=[weather.MINUTELY,weather.HOURLY,weather.DAILY], # default `[]`,
                timezone=None # default None - will be set by DarkSky API automatically
            )

            #Set up units [temp, wind speed,precip, storm distance]
            if forecast.flags.units in ["ca","si"]:
                self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]
            elif forecast.flags.units == "uk2":
                self.data.wx_units = ["C","mph","mm","miles","hPa","uk2"]
            else:
                self.data.wx_units = ["F","mph","in","miles","mbar","us"]
            
            if forecast.currently.wind_speed> 0:
                winddir = self.degrees_to_direction(forecast.currently.wind_bearing)
            else:
                winddir = self.degrees_to_direction(0)

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

            self.data.wx_current = [wx_timestamp,forecast.currently.icon,forecast.currently.summary,wx_temp ,wx_app_temp ,wx_humidity]

            wx_precip_prob = str(round(forecast.currently.precip_probability,1)*100) + "%"
            self.data.wx_curr_precip = [forecast.currently.precip_type,wx_precip_prob,forecast.currently.precip_intensity,forecast.currently.precipAccumulation]

            if self.show_alerts and len(forecast.alerts) > 0:
                wx_alert_time = forecast.alerts.time.strftime("%m/%d %H:%M:%S")
                wx_alert_expires = forecast.alerts.expires.strftime("%%m/%d %H:%M:%S")
                wx_storm_bearing = self.degrees_to_direction(forecast.currently.nearest_storm_bearing)
                wx_storm_distance = str(forecast.currently.nearest_storm_distance) + " " + self.data.wx_units[3]
                self.data.wx_alerts = [forecast.alerts.title,forecast.alerts.severity,forecast.alerts.regions,wx_alerts_time,wx_alert_expires,wx_storm_distance,wx_storm_bearing]
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
