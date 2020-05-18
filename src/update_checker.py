import sh
from sh import git
import time
import os, sys
import debug

class UpdateChecker(object):
    def __init__(self,data,scheduler):
        self.workingDir = os.getcwd()
        self.data = data

        self.CheckForUpdate()

        # Do a daily check @ 3AM
        scheduler.add_job(self.CheckForUpdate, 'cron', hour=3,minute=0)
        #Check every 5 mins for testing only
        #scheduler.add_job(self.CheckForUpdate, 'cron', minute='*/5')

    def CheckForUpdate(self):
        debug.info("Checking update status for " + self.workingDir + "...")
        updateRemote = git("--git-dir=" + self.workingDir + "/.git/", "--work-tree=" + self.workingDir,"remote", "update")
        statusCheck = git("--git-dir=" + self.workingDir + "/.git/", "--work-tree=" + self.workingDir, "status")

        if "up to date" in statusCheck or "up-to-date" in statusCheck:
            debug.info("Code up to date.")
            self.data.newUpdate = False
        else:
            debug.info("Update available.")
            self.data.newUpdate = True