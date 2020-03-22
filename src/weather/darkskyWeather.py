from darksky.api import DarkSky
from darksky.types import languages, units, weather
import debug
import geocoder
from time import sleep

API_KEY = '78c800007e066c9ccbd8162bcf5eb350'

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

            # Final wrapper identical for both ways
            #print(forecast.latitude) # 42.3601
            #print(forecast.longitude) # -71.0589
            #print(forecast.timezone) # timezone for coordinates. For exmaple: `America/New_York`

            # print(forecast.currently.time)
            # print(forecast.currently.temperature)
            # print(forecast.currently.apparent_temperature)
            # print(forecast.currently.humidity)
            # print(forecast.currently.pressure)
            # print(forecast.currently.summary)
            # print(forecast.currently.icon) # CurrentlyForecast. Can be found at darksky/forecast.py
            #forecast.minutely # MinutelyForecast. Can be found at darksky/forecast.py
            #print(forecast.hourly) # HourlyForecast. Can be found at darksky/forecast.py
            #forecast.daily # DailyForecast. Can be found at darksky/forecast.py
            #print(forecast.alerts) # [Alert]. Can be found at darksky/forecast.py

            #Loop through forecast keys and display values.  Only for Currently
            print(forecast.flags.units)
            #for key in forecast.currently:
            #    print(key)
            self.data.weather_current = [forecast.currently.time,forecast.currently.icon,forecast.currently.summary,forecast.currently.temperature,forecast.currently.apparent_temperature,forecast.currently.humidity]
            
            if self.show_alerts and len(forecast.alerts) > 0:
                self.data.weather_alerts = [forecast.alerts.title,forecast.alerts.severity,forecast.alerts.regions,forecast.alerts.time,forecast.alerts.expires,forecast.currently.nearest_storm_distance,forecast.currently.nearest_storm_bearing]
                self.weather_alert += 1
                self.sleepEvent.set()
                
                print(forecast.alerts.title)
                print(forecast.alerts.regions)
                print(forecast.alerts.severity)
                print(forecast.alerts.time)
                print(forecast.alerts.expires)
                #print(akey.description)
                #print(akey.uri)
            else:
                self.data.weather_alert_interrupt = False
                self.weather_alert = 0
            
            # Run every 'x' minutes
            sleep(60 * self.weather_frequency)
