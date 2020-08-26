from pyowm.owm import OWM
from env_canada import ECData
import debug
from datetime import datetime,timedelta
from random import randint
from time import sleep
from api.weather.wx_utils import cadhumidex, wind_chill, get_icons, degrees_to_direction, temp_f, wind_mph

class wxForecast(object):
    def __init__(self, data, scheduler):

        self.data = data
        self.weather_frequency = data.config.weather_update_freq
        self.time_format = data.config.time_format
        self.icons = get_icons("ecIcons_utf8.csv")
        self.network_issues = data.network_issues

        self.apikey = data.config.weather_owm_apikey

        self.currdate = datetime.now()
        self.max_days = data.config.weather_forecast_days


        if self.data.config.weather_data_feed.lower() == "ec":
            try:
                # sleep_time = randint(22,23)
                # debug.info("Randomly sleeping {} seconds before getting EC forecasts .....".format(sleep_time))
                # sleep(sleep_time)
                self.ecData = ECData(coordinates=(self.data.latlng))
            except (requests.exceptions) as e:
            #     #raise ValueError(e)
                debug.error("Unable to get EC forecast data error:{0}".format(e))
                self.data.forecast_updated = False
                self.network_issues = True
                pass

        if self.data.config.weather_data_feed.lower() == "owm":
            
            self.owm = OWM(self.apikey)
            self.owm_manager = self.owm.weather_manager()


        # Get forecast for next day every day, every 3 hours
        scheduler.add_job(self.GetForecast, 'cron', hour='*/3',minute=0)
        #Check every 5 mins for testing only
        #scheduler.add_job(self.GetForecast, 'cron', minute='*/5')

        #Set up units [temp, wind speed,precip, storm distance]
        #Use these eventhough some are included in data feed
        if self.data.config.weather_units == "metric":
            self.data.wx_units = ["C","kph","mm","miles","hPa","ca"]
        else:
            self.data.wx_units = ["F","mph","in","miles","MB","us"]
    
    def GetForecast(self):

        #self.data.wx_forecast = []
        wx_forecast = []

        # For testing
        #self.data.wx_forecast = [['Tue 08/25', 'Mainly Clear', '\uf02e', '-29C', '-14C'], ['Wed 08/26', 'Light Rain Shower', '\uf02b', '27C', '18C'], ['Thu 08/27', 'Clear', '\uf02e', '23C', '13C']]

        if self.data.config.weather_data_feed.lower() == "ec":
            debug.info("Refreshing EC daily weather forecast")
            self.ecData.update()

            forecasts = self.ecData.daily_forecasts

            #Loop through the data and create the forecast
            #Number of days to add to current day for the date string, this will be incremented
            index = 1
            forecast_day = 1
            while index <= self.max_days:
            #Create the date
                nextdate = self.currdate + timedelta(days=forecast_day)
                nextdate_name = nextdate.strftime("%A")
                nextdate = nextdate.strftime("%a %m/%d")  
                forecast_day += 1

                #Loop through forecast and get the day equal to nextdate_name
                for day_forecast in forecasts:
                    for k,v in day_forecast.items():
                        if k == "period" and v == nextdate_name:
                            #print(day_forecast)
                            summary = day_forecast['text_summary']
                            icon_code = day_forecast['icon_code']
                            temp_high = day_forecast['temperature'] + self.data.wx_units[0]
                            # Get the nextdate_name + " night"
                            night_forecast = next((sub for sub in forecasts if sub['period'] == nextdate_name + " night"), None)
                            temp_low = night_forecast['temperature'] + self.data.wx_units[0]
                
                if icon_code == None:
                    wx_icon = '\uf07b'
                    wx_summary = "N/A"
                else:
                    #Get condition and icon from dictionary
                    for row in range(len(self.icons)):
                        if int(self.icons[row]["ForecastCode"]) == int(icon_code):
                            wx_icon = self.icons[row]['font']
                            wx_summary = self.icons[row]['Description']
                            break
                        else:
                            wx_icon = '\uf07b'
                            wx_summary = "N/A"


                wx_forecast.append([nextdate,wx_summary,wx_icon,temp_high,temp_low])     
                index += 1



        if self.data.config.weather_data_feed.lower() == "owm":
            debug.info("Refreshing OWM daily weather forecast")
            #lat = self.data.latlng[0]
            #lon = self.data.latlng[1]
            one_call = self.owm_manager.one_call(lat=self.data.latlng[0],lon=self.data.latlng[1])

            index=1
            forecast = []
            while index <= self.max_days:
                nextdate = self.currdate + timedelta(days=index)
                nextdate = nextdate.strftime("%a %m/%d")
                icon_code = int(one_call.forecast_daily[index].weather_code)
                summary = one_call.forecast_daily[index].detailed_status
                if self.data.config.weather_units == "metric":
                    temp_high = one_call.forecast_daily[index].temperature('celsius').get('max', None) 
                    temp_low = one_call.forecast_daily[index].temperature('celsius').get('min', None)
                else:
                    temp_high = one_call.forecast_daily[index].temperature('fahrenheit').get('max', None) 
                    temp_low = one_call.forecast_daily[index].temperature('fahrenheit').get('min', None)

                #Round high and low temps to two digitrs only (ie 25 and not 25.61)
                temp_hi = str(round(float(temp_high))) + self.data.wx_units[0]
                temp_lo = str(round(float(temp_low))) + self.data.wx_units[0]

                if icon_code in range(200,299):
                    # Thunderstorm Class
                    owm_icon = 200
                elif icon_code in range(300,399):
                    # Drizzle Class
                    owm_icon = 300
                elif icon_code in range(500,599):
                    # Rain Class
                    owm_icon = 500
                elif icon_code in range(600,699):
                    # Rain Class
                    owm_icon = 600
                elif icon_code in range(800,805):
                    # Rain Class
                    owm_icon = 801
                else:
                    owm_icon = icon_code 

                #Get the icon, only for the day
                if icon_code == None:
                    wx_icon = '\uf07b'
                    wx_summary = "N/A"
                else:
                    #Get condition and icon from dictionary
                    for row in range(len(self.icons)):
                        if int(self.icons[row]["OWMCode"]) == owm_icon:
                            wx_icon = self.icons[row]['font']
                            wx_summary = self.icons[row]['Description']
                            break
                        else:
                            wx_icon = '\uf07b'
                            wx_summary = "N/A"

                wx_forecast.append([nextdate,summary,wx_icon,temp_hi,temp_lo])
                index += 1

        if self.data.wx_forecast != wx_forecast:
            debug.info("Forecast has changed and been updated....")
            self.data.wx_forecast = wx_forecast
        
        self.data.forecast_updated = True
        self.network_issues = False

        debug.info(self.data.wx_forecast)
