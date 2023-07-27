import debug
from datetime import datetime,date,time,timedelta
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

        self.startsaver = None
        self.stopsaver = None
        self.shifted_time = None

        if len(data.config.screensaver_start) > 0:
            timeCheck = timeValidator(data.config.screensaver_start)
            if timeCheck == "12h":
                self.startsaver = datetime.strptime(data.config.screensaver_start, '%I:%M %p').time()
            elif timeCheck == "24h":
                self.startsaver = datetime.strptime(data.config.screensaver_start, '%H:%M').time()
            else:
                debug.error("Start time setting ({}) for screen saver is not a valid 12h or 24h format. Screen saver will not be used".format(data.config.screensaver_start))


        if len(data.config.screensaver_stop) > 0:
            timeCheck = timeValidator(data.config.screensaver_stop)
            if timeCheck == "12h":
                self.stopsaver = datetime.strptime(data.config.screensaver_stop, '%I:%M %p').time()
            elif timeCheck == "24h":
                self.stopsaver = datetime.strptime(data.config.screensaver_stop, '%H:%M').time()
            else:
                debug.error("Stop time setting ({}) for screensaver is not a valid 12h or 24h format. Screen saver will not be used".format(data.config.screensaver_stop))

        if self.startsaver and self.stopsaver is not None:
            self.shifted_time = datetime.time(datetime.now() + timedelta(minutes=5))
            # Check to see if the current time is greater than start time but less than stop time.  If so, change the start time hour and min
            if (self.shifted_time > self.startsaver):
                scheduler.add_job(self.runSaver, 'cron', hour=self.shifted_time.hour,minute=self.shifted_time.minute,id='screenSaverON',misfire_grace_time=None)
            else:    
                scheduler.add_job(self.runSaver, 'cron', hour=self.startsaver.hour,minute=self.startsaver.minute,id='screenSaverON',misfire_grace_time=None)
                
            scheduler.add_job(self.stopSaver, 'cron', hour=self.stopsaver.hour, minute=self.stopsaver.minute,id='screenSaverOFF',misfire_grace_time=None)
            startrun = self.scheduler.get_job('screenSaverON').next_run_time
            stoprun = self.scheduler.get_job('screenSaverOFF').next_run_time
            debug.info("Screen saver will start @ {} and end @ {}".format(startrun,stoprun))
        else:
            debug.error("Start or Stop time setting for screensaver is not a valid 12h or 24h format. Screen saver will not be used, check the config.json")

    def runSaver(self):
        #Launch screen saver board, then Fade off brightness to 0

        if not self.data.screensaver_livegame:
            if self.data.curr_board is not None:
                debug.info("Screen saver started.... Currently displayed board " + self.data.curr_board)
            else:
                debug.info("Screen saver started.... Currently displayed board is not set")
                
            self.data.screensaver = True
            self.sleepEvent.set()
            #Set screen saver back to normal time and reschedule the job
            self.scheduler.reschedule_job('screenSaverON', trigger='cron', hour=self.startsaver.hour,minute=self.startsaver.minute)
            # Shut down all scheduled jobs (except for screensaver ones)
            if not self.data.config.screensaver_data_updates:
                alljobs = self.scheduler.get_jobs()
                #Loop through the jobs and pause if not named screenSaverOn or screenSaverOFF
                debug.info("Pausing all scheduled jobs while screensaver active")
                for job in alljobs:
                    if "screenSaver" not in job.id:
                        job.pause()
        else:
            # Add shifting code to change the runSaver time so it will start once game is done
            # Shift time by 5 mins
            self.shifted_time = datetime.time(datetime.now() + timedelta(minutes=5))
            self.scheduler.reschedule_job('screenSaverON', trigger='cron', hour=self.shifted_time.hour,minute=self.shifted_time.minute)
            new_run = self.scheduler.get_job('screenSaverON').next_run_time
            debug.error("Screen saver not started.... game is scheduled or live! Will try again @ {}".format(new_run))

        

    def stopSaver(self):
        #Stop screen saver board, Fade brightness back to last setting
        if self.data.prev_board is not None:
            debug.info("Screen saver stopped.... Starting next displayed board " + self.data.prev_board)
        else:
            debug.info("Screen saver stopped.... Starting next displayed board (not set)")

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

        # If user doesn't use dimmer or brightness on command line, don't fade in
        if self.original_brightness is not None:
            while i <= self.original_brightness:
                self.matrix.set_brightness(i)
                i += 1
                sleep(0.1)

