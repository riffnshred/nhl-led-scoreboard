import debug
from gpiozero import MotionSensor
from signal import pause
from threading import Timer
import time
from sbio.screensaver import screenSaver

class Motion(object):
    def __init__(self, data, matrix,sleepEvent,scheduler,screenSaver):
        self.data = data
        self.matrix = matrix
        self.ms_run = True
        self.sleepEvent = sleepEvent
        self.screensaver = screenSaver

        self.pir = MotionSensor(self.data.config.screensaver_ms_pin)

        self.pir.when_motion = self.motion_func
        self.pir.when_no_motion = self.no_motion_func

        #Delay to wait before motion is considered to have stopped completely
        self.delay_time = self.data.config.screensaver_ms_delay
        self.delay_enabled = False
        self.off_timer = None
        self.ssOff_trigger = False

    def screenSaverOn(self):
        if self.ssOff_trigger:
            debug.warning("No Motion triggered...screen saver being turned on")
            self.ssOff_trigger = False
            self.screensaver.runSaver()
        else:
            debug.warning("Ignoring no motion, screen saver not active")

    def screenSaverOff(self):
        if self.data.screensaver_displayed and self.data.screensaver and not self.data.pb_trigger:
            debug.warning("Motion triggered...screen saver being turned off")
            self.ssOff_trigger = True
            self.screensaver.stopSaver()
        else:
            debug.warning("Ignoring motion, screen saver not active")

    def cancel_timer(self):
        if self.off_timer is not None:
            self.off_timer.cancel()
            self.off_timer = None

    def motion_func(self):
        self.cancel_timer() # new motion detected, so we don't want the screen saver on yet
        self.screenSaverOff()

    def no_motion_func(self):
        self.cancel_timer() # cancel the old timer because we're about to create a new one
        self.off_timer = Timer(self.delay_time, self.screenSaverOn)  #turn on screen saver after delay
        self.off_timer.start()

    def run(self):
        if self.ms_run:
            pause() # wait forever
        else:
            pass