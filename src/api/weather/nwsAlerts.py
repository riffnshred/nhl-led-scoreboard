from noaa_sdk import noaa
import debug
import datetime
import json
import requests
from time import sleep
from api.weather.wx_utils import get_csv

BASE_URL = 'https://api.weather.gov/'
REQUEST_TIMEOUT = 5

# Code borrowed from https://github.com/dcshoecomp/noaa_alerts
# A sensor created for Home Assistant.

class nwsWxAlerts(object):
    def __init__(self, data, scheduler,sleepEvent):
        
        self.data = data
        self.sleepEvent = sleepEvent
        self.time_format = data.config.time_format
        self.alert_frequency = data.config.wxalert_update_freq
        self.weather_alert = 0
        # Date format 2020-04-19T13:56:00-05:00
        self.alert_date_format = "%Y-%m-%dT%H:%M:%S%z"
        self.lat = self.data.latlng[0]
        self.lon = self.data.latlng[1]
        self.network_issues = False
        
        self.nws_colors = get_csv("nws_colors.csv")

        #Testing
        #self.lat = 36.50
        #self.lon = -94.62
        #debug.info("Testing for " + str(self.lat) + "," + str(self.lon))

        scheduler.add_job(self.getAlerts, 'interval', minutes=self.alert_frequency,jitter=90,id='nwsAlerts')
        #Check every 5 mins for testing only
        #scheduler.add_job(self.CheckForUpdate, 'cron', minute='*/5')

        #Get initial Alerts
        self.getAlerts()
    
    def sortedbyurgencyandseverity(self,prop):
        if (prop['urgency']).lower() == 'immediate':
            sortedvalue = 1
        elif (prop['urgency']).lower() == 'expected':
            sortedvalue = 10
        elif (prop['urgency']).lower() == 'future':
            sortedvalue = 100
        else:
            sortedvalue = 1000
        if (prop['severity']).lower() == 'extreme':
            sortedvalue = sortedvalue * 1
        elif (prop['severity']).lower() == 'severe':
            sortedvalue = sortedvalue * 2
        elif (prop['severity']).lower() == 'moderate':
            sortedvalue = sortedvalue * 3
        else:
            sortedvalue = sortedvalue * 4
        return sortedvalue


    
    def getAlerts(self):
        
        
        params={'point': '{0},{1}'.format(self.lat,self.lon)}
        self.network_issues = False
        
        #See if the api.weather.gov site is available, if not throw error code and jump out of loop
        try:
            r = requests.get(BASE_URL, timeout=REQUEST_TIMEOUT)
            debug.info("NWS alerts {} returned status code: {}".format(BASE_URL,r.status_code))
        except requests.exceptions as e:
            #raise ValueError(e)
            debug.error(e)
            self.network_issues = True
            pass

        if not self.network_issues:
            try:
                debug.info("Checking NWS weather alerts")
                nws = noaa.NOAA().alerts(active=1, **params)
                #debug.info(nws)
            except Exception as err:
                debug.error(err)
                self.network_issues = True
                pass
            #print (nws)
        if not self.network_issues:
            nwsalerts = []

            for alert in nws['features'] :
                        nwsalerts.append(alert['properties'])
            _state = len(nwsalerts)
            debug.info("Number of alerts is " + str(_state))

            if _state > 0:
                _attributes = {}
                _attributes['alerts'] = sorted(nwsalerts, key=self.sortedbyurgencyandseverity)
                _attributes['urgency'] = _attributes['alerts'][0]['urgency'] if _state > 0 else None
                _attributes['event_severity'] = _attributes['alerts'][0]['severity'] if _state > 0 else None
                _attributes['event'] = _attributes['alerts'][0]['event'] if _state > 0 else None
                _attributes['description'] = _attributes['alerts'][0]['description'] if _state > 0 else None
                _attributes['headline'] = _attributes['alerts'][0]['headline'] if _state > 0 else None
                _attributes['instruction'] = _attributes['alerts'][0]['instruction'] if _state > 0 else None
                _attributes['effective'] = _attributes['alerts'][0]['effective'] if _state > 0 else None
                _attributes['expires'] = _attributes['alerts'][0]['expires'] if _state > 0 else None
                _attributes['alerts_string'] = json.dumps(_attributes['alerts'])

                # Build up the weather alert string
                # urgency	(Immediate, Expected, Future, Unknown)
                # severity	severity level(minor, moderate, severe, extreme)
                # 
                if self.data.config.wxalert_nws_show_expire and _attributes['expires'] != None:
                    warn_date = _attributes['expires']
                else:
                    warn_date = _attributes['effective']
                    
                #Convert to date for display
                warn_datetime = datetime.datetime.strptime(warn_date,self.alert_date_format)
                if self.time_format == "%H:%M":
                    wx_alert_time = warn_datetime.strftime("%m/%d %H:%M")
                else:
                    wx_alert_time = warn_datetime.strftime("%m/%d %I:%M %p")
                #debug.info(_attributes['event'])
                #Strip out the string at end of string for the title
                #Loop through the csv with the event and match to get the color
                
                for row in range(len(self.nws_colors)):
                    if self.nws_colors[row]["Event"] == _attributes['event']:
                        colorstr = self.nws_colors[row]['Color']
                        wx_alertcolor = tuple(map(int, colorstr.split(',')))
                        break
                    else:
                        wx_alertcolor = (0,0,0)
                
                debug.info("NWS Alert ({}) has color: {}".format(_attributes['event'],wx_alertcolor))
                if "Warning" in _attributes['event']:
                    wx_alert_title = _attributes['event'][:-(len(" Warning"))] 
                    wx_type = "warning"
                elif "Watch" in _attributes['event']:
                    wx_alert_title = _attributes['event'][:-(len(" Watch"))]
                    wx_type = "watch"
                elif "Advisory" in _attributes['event']:
                    wx_alert_title = _attributes['event'][:-(len(" Advisory"))]
                    wx_type = "advisory"
                else:
                    wx_alert_title = _attributes['event']
                    wx_type = "statement"
                

                # Only create an alert for Immediate and Expected?

                if wx_type != "statement":
                    self.data.wx_alerts = [wx_alert_title,wx_type,wx_alert_time,_attributes['urgency'],_attributes['event_severity'],wx_alertcolor]
                    # Only interrupt the first time
                    if self.weather_alert == 0 and self.data.wx_updated:
                        self.data.wx_alert_interrupt = True
                        self.sleepEvent.set()
                    self.weather_alert += 1

                    debug.info(self.data.wx_alerts)
                else:
                    self.data.wx_alert_interrupt = False
                    self.weather_alert = 0
                    self.data.wx_alerts = []
                    debug.info("No active NWS alerts in your area")
            
            else:
                self.data.wx_alert_interrupt = False
                self.weather_alert = 0
                self.data.wx_alerts = []
                debug.info("No active NWS alerts in your area")

            
            # Run every 'x' minutes
            #sleep(60 * self.alert_frequency)
