from gpiozero import MotionSensor
import debug
from datetime import datetime,timedelta
from time import sleep

class screenSaver(object):
    def __init__(self, data, sleepEvent, scheduler):

        # pir = MotionSensor(15)

        # pir.wait_for_motion()
        # print("Motion detected!")

        self.data = data
        self.matrix = matrix
        self.scheduler = scheduler
        self.sleepEvent = sleepEvent

        scheduler.add_job(self.runSaver, 'cron', minutes=self.weather_frequency,jitter=60,id='screenSaverON')
        scheduler.add_job(self.stopSaver, 'cron', minutes=self.weather_frequency,jitter=60,id='screenSaverOFF')
        

        #Get initial obs
        self.getWeather()

    def runSaver(self):
        #Launch screen saver board, then Fade off brightness to 0
        debug.info("Screen saver started.... Currently displayed board " + self.data.curr_board)
        self.data.screensaver = True
        self.sleepEvent.set()

        curr_brightness = self.brightness
        

    def stopSaver(self):
        #Stop screen saver board, Fade in brightness back to last setting
        debug.info("Screen saver stopped.... Currently displayed board " + self.data.curr_board)
        self.data.screensaver = False
        self.sleepEvent.clear()


