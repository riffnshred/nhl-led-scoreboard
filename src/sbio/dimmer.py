import ephem
import debug
from python_tsl2591 import tsl2591
from datetime import datetime,date,time
from utils import timeValidator
from time import sleep

class Dimmer(object):
    def __init__(self, data, matrix,scheduler):
        self._observer = ephem.Observer()
        self._observer.pressure = 0
        self._observer.horizon = '-6'

        self.brightness = 1
        self.matrix = matrix
        self.data = data

        self._observer.lat = str(self.data.latlng[0])
        self._observer.lon = str(self.data.latlng[1])
       
        if data.config.dimmer_mode == "always":
           self.mode = True
        else:
           self.mode = False

        #If selected hardware, attempt to initialize sensor
        self.luxsensor = False

        # Make sure brightness values are not less than 0 or higher than 100
        if data.config.dimmer_sunset_brightness < 0:
            data.config.dimmer_sunset_brightness = 0
        if data.config.dimmer_sunset_brightness > 100:
            data.config.dimmer_sunset_brightness = 100

        if data.config.dimmer_sunrise_brightness  < 0:
            data.config.dimmer_sunrise_brightness = 0
        if data.config.dimmer_sunrise_brightness > 100:
            data.config.dimmer_sunrise_brightness = 100

        if data.config.dimmer_source == "hardware":
            try:
                self.tsl = tsl2591()  # initialize
                self.luxsensor = True
            except:
                debug.error("Light sensor not found or not connected, falling back to software mode")
                self.luxsensor = False
                # Fall back to using software mode
                self.data.config.dimmer_source = "software"

        # Light level in lux from config file
        self.lux = self.data.config.dimmer_light_level_lux

        self.daytime = None
        self.nighttime = None

        #User set times to start and end dimmer at, comes from the config.json
        if len(data.config.dimmer_daytime) > 0:
            timeCheck = timeValidator(data.config.dimmer_daytime)
            if timeCheck == "12h":
                self.daytime = datetime.strptime(data.config.dimmer_daytime, '%I:%M %p').time()
            elif timeCheck == "24h":
                self.daytime = datetime.strptime(data.config.dimmer_daytime, '%H:%M').time() 
            else:
                debug.error("Daytime setting ({}) for dimmer is not a valid 12h or 24h format.  Will use location for sunrise".format(data.config.dimmer_daytime))
            

        if len(data.config.dimmer_nighttime) > 0:
            timeCheck = timeValidator(data.config.dimmer_nighttime)
            if timeCheck == "12h":
                self.nighttime = datetime.strptime(data.config.dimmer_nighttime, '%I:%M %p').time()
            elif timeCheck == "24h":
                self.nighttime = datetime.strptime(data.config.dimmer_nighttime, '%H:%M').time() 
            else:
                debug.error("Night time setting ({}) for dimmer is not a valid 12h or 24h format.  Will use location for sunset".format(data.config.dimmer_nighttime))

        scheduler.add_job(self.checkDimmer, 'interval', minutes=self.data.config.dimmer_frequency,jitter=60,id='Dimmer')
        #Check every 5 mins for testing only
        #scheduler.add_job(self.CheckForUpdate, 'cron', minute='*/5')

        #Set initial brightness 
        self.checkDimmer()
    
    def checkDimmer(self):
        debug.info("Using " + self.data.config.dimmer_source + " to determine dimming" )
        #debug.info(self.mode)
        #while True:
        debug.info("Checking for dimmer") 
        # Only run if off day or override by config (dimmer mode = always)
        if (not self.data.config.live_mode or self.data.is_pref_team_offday() or self.data.is_nhl_offday() or self.mode):
            if not self.luxsensor:
                debug.info("Using " + self.data.config.dimmer_source + " to determine dimming" )
                #self._observer.date = ephem.now()
                currtime = datetime.strptime(ephem.localtime(ephem.now()).strftime("%H:%M"),"%H:%M").time()
                currdate = datetime.strptime(ephem.localtime(ephem.now()).strftime("%y-%m-%d"),"%y-%m-%d").date()
                
                if self.daytime and self.nighttime is not None:
                    debug.info("Using set times for dimmer currtime: {} currdate: {} daytime: {} nighttime: {}".format(currtime, currdate, self.daytime,self.nighttime))

                    if currtime >= self.daytime and currtime < self.nighttime:
                        debug.info("It is day time")
                        self.brightness = self.data.config.dimmer_sunrise_brightness
                    
                    if currtime > self.nighttime and currtime < self.daytime:
                        debug.info("It is night time")
                        self.brightness = self.data.config.dimmer_sunset_brightness 

                else:

                    morning = self._observer.next_rising(ephem.Sun(), use_center=True)
                    night = self._observer.next_setting(ephem.Sun(), use_center=True)
                    #sunrise = ephem.localtime(morning)
                    #sunset = ephem.localtime(night)
                    #debug.info(sunrise)
                    #debug.info(sunset)

                    debug.warning("Using ephem for dimmer:  Sunset is @ {}  Sunrise is @ {}".format(ephem.localtime(night),ephem.localtime(morning)))

                    # Very simplistic way of handling the day/night but it works
                    if morning < night:
                        # Morning is sooner, so it must be night
                        debug.info("It is night time")
                        self.brightness = self.data.config.dimmer_sunset_brightness 
                    else:
                        debug.info("It is day time")
                        
                        self.brightness = self.data.config.dimmer_sunrise_brightness
            else: 
                # This is where code for light sensor will go.
                # This will be for a TSL2591 sensor (see https://www.adafruit.com/product/1980)
                debug.info("Using " + self.data.config.dimmer_source + " to determine dimming" )
                if self.luxsensor: 
                    # Read current value of light, and adjust brightness level based on that
                    full, ir = self.tsl.get_full_luminosity()
                    lux = self.tsl.calculate_lux(full, ir)
                    debug.info("Ambient light level = " + str(lux) + " lux")
                    #Using a lux value>=400 for sunrise (see https://en.wikipedia.org/wiki/Lux), set up brightness
                    #Some actual testing in your environment might be needed to adjust lux values and what you
                    #want for brightness.  The below simulates sunrise/sunset with sunset having lower brightness
                    if lux >= self.lux:
                        self.brightness = self.data.config.dimmer_sunrise_brightness
                    else:
                        self.brightness = self.data.config.dimmer_sunset_brightness

            self.matrix.set_brightness(self.brightness)
            #self.matrix.render()
        else:
            debug.info("No dimming...Live Game on?")
            # Run every 5 minutes
            #sleep(60 * self.data.config.dimmer_frequency)
