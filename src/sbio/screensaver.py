import debug
from datetime import datetime,date,time
from utils import timeValidator
from time import sleep

class screenSaver(object):
    def __init__(self, data, matrix,sleepEvent, scheduler):

        self.data = data
        self.matrix = matrix
        self.brightness = self.matrix.brightness
        self.original_brightness = self.brightness
        self.scheduler = scheduler
        self.sleepEvent = sleepEvent

        #User set times to start and end dimmer at, comes from the config.json

        startsaver = None
        stopsaver = None

        if len(data.config.screensaver_start) > 0:
            timeCheck = timeValidator(data.config.screensaver_start)
            if timeCheck == "12h":
                startsaver = datetime.strptime(data.config.screensaver_start, '%I:%M %p').time()
            elif timeCheck == "24h":
                startsaver = datetime.strptime(data.config.screensaver_start, '%H:%M').time()
            else:
                debug.error("Start time setting ({}) for screen saver is not a valid 12h or 24h format. Screen saver will not be used".format(data.config.screensaver_start))


        if len(data.config.screensaver_stop) > 0:
            timeCheck = timeValidator(data.config.screensaver_stop)
            if timeCheck == "12h":
                stopsaver = datetime.strptime(data.config.screensaver_stop, '%I:%M %p').time()
            elif timeCheck == "24h":
                stopsaver = datetime.strptime(data.config.screensaver_stop, '%H:%M').time()
            else:
                debug.error("Stop time setting ({}) for screensaver is not a valid 12h or 24h format. Screen saver will not be used".format(data.config.screensaver_stop))

        if startsaver and stopsaver is not None:
            scheduler.add_job(self.runSaver, 'cron', hour=startsaver.hour,minute=startsaver.minute,id='screenSaverON')
            scheduler.add_job(self.stopSaver, 'cron', hour=stopsaver.hour, minute=stopsaver.minute,id='screenSaverOFF')
            startrun = self.scheduler.get_job('screenSaverON').next_run_time
            stoprun = self.scheduler.get_job('screenSaverOFF').next_run_time
            debug.info("Screen saver will start @ {} and end @ {}".format(startrun.strftime("%H:%M"),stoprun.strftime("%H:%M")))
        else:
            debug.error("Start or Stop time setting for screensaver is not a valid 12h or 24h format. Screen saver will not be used, check the config.json")

    def runSaver(self):
        #Launch screen saver board, then Fade off brightness to 0
        if not self.data.screensaver_livegame:
            debug.info("Screen saver started.... Currently displayed board " + self.data.curr_board)
            self.data.screensaver = True
            self.sleepEvent.set()
        else:
            debug.error("Screen saver not started.... we are in a live game!")

        # Shut down all scheduled jobs (except for screensaver ones)
        if not self.data.config.screensaver_data_updates:
            alljobs = self.scheduler.get_jobs()
            #debug.info(alljobs)
            #Loop through the jobs and pause if not named screenSaverOn or screenSaverOFF
            debug.info("Pausing all scheduled jobs while screensaver active")
            for job in alljobs:
                if "screenSaver" not in job.id:
                    job.pause()

    def stopSaver(self):
        #Stop screen saver board, Fade brightness back to last setting
        debug.info("Screen saver stopped.... Starting next displayed board " + self.data.prev_board)

        #Resume all paused jobs
        if not self.data.config.screensaver_data_updates:
            alljobs = self.scheduler.get_jobs()
            #debug.info(alljobs)
            #Loop through the jobs and resume if not named screenSaverOn or screenSaverOFF
            debug.info("Resuming all paused jobs while screensaver off")
            for job in alljobs:
                if "screenSaver" not in job.id:
                    job.resume()

        self.data.screensaver = False
        self.data.screensaver_displayed = False
        self.sleepEvent.set()

        i = 0

        while i <= self.original_brightness:
            self.matrix.set_brightness(i)
            i += 1
            sleep(0.1)

