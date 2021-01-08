import time
import os, sys
import debug
from lastversion import lastversion
from packaging import version

class UpdateChecker(object):
    def __init__(self,data,scheduler,ghtoken):

        self.scheduler = scheduler
        self.token = ghtoken
        self.workingDir = os.getcwd()
        self.versionFile = os.path.join(self.workingDir,'VERSION')
        self.data = data
        self.version = ""

        #Get installed version by reading VERSION file located in cwd
        if os.path.exists(self.versionFile):
            try:
                with open(self.versionFile) as versionFile:
                    self.version = versionFile.read().strip()
            except OSError:
                debug.error("Unable to open {}".format(self.versionFile))
        else:
            debug.error("File {} does not exist.".format(self.versionFile))

        if self.version != "":
            # Do a daily check @ 3AM
            scheduler.add_job(self.CheckForUpdate, 'cron', hour=3,minute=0,id='updatecheck')
            #Check every 5 mins for testing only
            #scheduler.add_job(self.CheckForUpdate, 'cron', minute='*/5')
            self.CheckForUpdate()

    def CheckForUpdate(self):
        debug.info("Checking for new release. {} v{} installed in {}".format(self.data.UpdateRepo,self.version,self.workingDir))

        #Use GITHUB Token to remove rate limit, not required if you are doing a single test per day
        os.environ['GITHUB_API_TOKEN'] = self.token
        debug.info("Using github api token: {} to check updates".format(self.token))
        # Use lastversion to check against github latest release repo, don't look at pre releases
        try:
            latest_version = lastversion.latest(self.data.UpdateRepo, output_format='version', pre_ok=False)
        except Exception as e:
            debug.error("Unable to get info from GitHub.  Error: {}".format(e))
        else:
            if latest_version != None:
                if latest_version > version.parse(self.version):
                    debug.info("New release v{} available.".format(latest_version))
                    self.data.newUpdate = True
                else:
                    debug.info("No new release.")
                    self.data.newUpdate = False
            else:
                debug.error("Unable to get latest version from github, is it tagged properly?")        
        nextcheck = self.scheduler.get_job('updatecheck').next_run_time

        debug.info("Next check for update @ {}".format(nextcheck))

        
        