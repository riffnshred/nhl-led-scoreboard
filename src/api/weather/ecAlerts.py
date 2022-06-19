from env_canada import ECWeather
import debug
import datetime
from time import sleep
import asyncio

class ecWxAlerts(object):
    def __init__(self, data, scheduler,sleepEvent):
        
        self.data = data
        self.time_format = data.config.time_format
        self.alert_frequency = data.config.wxalert_update_freq
        self.weather_alert = 0
        # Date format Friday April 03, 2020 at 04:36 CDT
        # Strip off the last 4 caharacters in the date string to remove timezone
        self.alert_date_format = "%A %B %d, %Y at %H:%M"
        self.network_issues = data.network_issues

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        scheduler.add_job(self.getAlerts, 'interval', minutes=self.alert_frequency,jitter=90,id='ecAlerts')
        #Check every 5 mins for testing only
        #scheduler.add_job(self.CheckForUpdate, 'cron', minute='*/5')

        #Get initial Alerts
        self.getAlerts()

    def getAlerts(self):


        debug.info("Checking for EC weather alerts")
        #ecData = ECData(coordinates=(self.data.latlng))
        asyncio.run(self.data.ecData.update())
        curr_alerts = self.data.ecData.alerts
        self.network_issues = False


        debug.info("Last Alert: {0}".format(self.data.wx_alerts))
        # Check if there's more than a length of 5 returned back as if there's
        # No alerts, the dictionary still comes back with empty values for 
        # warning, watch, advisory, statements and endings
        # Currently don't do anything with a statement
        #debug.info(curr_alerts)

        #Find the latest date in the curr_alerts


        try:
            len_warn = len(curr_alerts.get("warnings").get("value"))
            len_watch = len(curr_alerts.get("watches").get("value"))
            len_advisory = len(curr_alerts.get("advisories").get("value"))
        except:
            len_warn = 0
            len_watch = 0
            len_advisory = 0

        num_alerts = len_warn + len_watch + len_advisory

        if num_alerts > 0:
            # Only get the latest alert
            i = 0
            # Create the warnings, watches and advisory lists from curr_alerts but only take the most recent one

            wx_num_endings = len(curr_alerts.get("endings").get("value","0"))
            wx_num_warning = len(curr_alerts.get("warnings").get("value","0"))
            wx_num_watch = len(curr_alerts.get("watches").get("value","0"))
            wx_num_advisory = len(curr_alerts.get("advisories").get("value","0"))

            wx_total_alerts = wx_num_endings + wx_num_warning + wx_num_watch + wx_num_advisory
            warn_datetime = 0
            watch_datetime = 0
            advisory_datetime = 0
            warning = []
            watch = []
            advisory = []
            alerts = []

            if wx_num_warning > 0:
                warn_date = curr_alerts["warnings"]["value"][i]["date"][:-4]
                #Convert to date for display
                warn_datetime = datetime.datetime.strptime(warn_date,self.alert_date_format)
                if self.time_format == "%H:%M":
                    wx_alert_time = warn_datetime.strftime("%m/%d %H:%M")
                else:
                    wx_alert_time = warn_datetime.strftime("%m/%d %I:%M %p")
                #Strip out the Warning at end of string for the title
                wx_alert_title = curr_alerts["warnings"]["value"][i]["title"][:-(len(" Warning"))]
                warning = [wx_alert_title,"warning",wx_alert_time]
                alerts.append(warning)



            if wx_num_watch > 0:
                watch_date = curr_alerts["watches"]["value"][i]["date"][:-4]
                #Convert to date for display
                watch_datetime = datetime.datetime.strptime(watch_date,self.alert_date_format)
                if self.time_format == "%H:%M":
                    wx_alert_time = watch_datetime.strftime("%m/%d %H:%M")
                else:
                    wx_alert_time = watch_datetime.strftime("%m/%d %I:%M %p")
                wx_alert_title = curr_alerts["watches"]["value"][i]["title"][:-(len(" Watch"))]
                watch = [wx_alert_title,"watch",wx_alert_time]
                alerts.append(watch)



            if wx_num_advisory > 0:
                advisory_date = curr_alerts["advisories"]["value"][i]["date"][:-4]
                #Convert to date for display
                advisory_datetime = datetime.datetime.strptime(advisory_date,self.alert_date_format)

                if self.time_format == "%H:%M":
                    wx_alert_time = advisory_datetime.strftime("%m/%d %H:%M")
                else:
                    wx_alert_time = advisory_datetime.strftime("%m/%d %I:%M %p")

                wx_alert_title = curr_alerts["advisories"]["value"][i]["title"][:-(len(" Advisory"))]
                advisory = [wx_alert_title,"advisory",wx_alert_time]
                alerts.append(advisory)


            #Find the latest alert time to set what the alert should be shown
            #debug.info(alerts)
            alerts.sort(key = lambda x: x[2],reverse=True)


            if alerts[0][0] == "Severe Thunderstorm":
                alerts[0][0] = "Svr T-Storm"
            if alerts[0][0] == "Freezing Rain":
                alerts[0][0] = "Frzn Rain"
            if alerts[0][0] == "Freezing Drizzle":
                alerts[0][0] = "Frzn Drzl"

            #debug.info(alerts)

            if self.data.wx_alerts != alerts[0]:
                self.data.wx_alerts = alerts[0]
                self.weather_alert = 0

            if wx_num_endings > 0:
                ending_date = curr_alerts["endings"]["value"][i]["date"][:-4]
                #Convert to date for display
                ending_datetime = datetime.datetime.strptime(ending_date,self.alert_date_format)
                if self.time_format == "%H:%M":
                    wx_alert_time = ending_datetime.strftime("%m/%d %H:%M")
                else:
                    wx_alert_time = ending_datetime.strftime("%m/%d %I:%M %p")

                endings = [curr_alerts["endings"]["value"][i]["title"],"ended",wx_alert_time]
                self.data.wx_alert_interrupt = False
                self.weather_alert = 0
                self.data.wx_alerts = []
                debug.info(endings)
            # else:
            #     self.data.wx_alert_interrupt = False
            #     self.weather_alert = 0

            if len(self.data.wx_alerts) > 0:
                debug.info("Current Alert: {0}".format(self.data.wx_alerts))

            if wx_num_endings == 0:
                if self.weather_alert == 0:
                    self.data.wx_alert_interrupt = True
                    self.sleepEvent.set()
                self.weather_alert += 1


        else:
            debug.info("No active EC weather alerts in your area")
            self.data.wx_alert_interrupt = False
            self.data.wx_alerts.clear()
            self.weather_alert = 0
            # Run every 'x' minutes
            #sleep(60 * self.alert_frequency)
