import ephem
import debug
import geocoder
from time import sleep

class Dimmer(object):
    def __init__(self, data, matrix):
        self._observer = ephem.Observer()
        self._observer.pressure = 0
        self._observer.horizon = '-6'

        # Use geocoder library to get lat/lon
        g = geocoder.ip('me')
        debug.info("location for sunrise/sunset is: " + str(g.latlng))
        self._observer.lat = str(g.lat)
        self._observer.lon = str(g.lng)

        self.brightness = 1
        self.matrix = matrix
        self.data = data

    def run(self):
        while True:
            debug.info("Checking for dimmer") 
            # Only run if off day
            if (not self.data.config.live_mode or self.data.is_pref_team_offday() or self.data.is_nhl_offday()):
               self._observer.date = ephem.now()
               #lt = ephem.localtime(self._observer.date)
               #debug.info(lt)
               morning = self._observer.next_rising(ephem.Sun(), use_center=True)
               night = self._observer.next_setting(ephem.Sun(), use_center=True)
               #sunrise = ephem.localtime(morning)
               #sunset = ephem.localtime(night)
               #debug.info(sunrise)
               #debug.info(sunset)

               # Very simplistic way of handling the day/night but it works
               if morning < night:
                   # Morning is sooner, so it must be night
                   debug.info("It is night time")
                   self.brightness = 5
               else:
                   debug.info("It is day time")
                   self.brightness = 50
            
               self.matrix.set_brightness(self.brightness)
               self.matrix.render()
            else:
               debug.info("No dimming...Live Game on?")
            # Run every 5 minutes
            sleep(60 * 5)
