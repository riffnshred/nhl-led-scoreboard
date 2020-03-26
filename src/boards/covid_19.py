from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from datetime import datetime, timedelta
from utils import convert_time
import random

class Covid_19:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        self.data.covid19.get_all()
        if data.config.covid_ww_board_enabled:
            try:
                self.worldwide_data = self.data.covid19.ww
                self.data.network_issues = False
            except ValueError as e:
                print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                self.data.network_issues = True

        if data.config.covid_country_board_enabled:
            self.country = data.config.covid_country
            try:
                self.data.network_issues = False
                self.country_data = self.data.covid19.countrydict[self.country]
            except ValueError as e:
                print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                self.data.network_issues = True

        if data.config.covid_us_state_board_enabled:
            self.us_state = data.config.covid_us_state
            try:
                self.data.network_issues = False
                self.us_state_data = self.data.covid19.us_state_dict[self.us_state]
            except ValueError as e:
                print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                self.data.network_issues = True
           

        self.layout = self.data.config.config.layout.get_board_layout('covid_19')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        #self.last_update = convert_time((datetime(1970, 1, 1) + timedelta(milliseconds=self.worldwide_data['updated'])).strftime("%Y-%m-%dT%H:%M:%SZ")).strftime("%m/%d %H:%M:%S")
        self.last_update = datetime.now().strftime("%m/%d %H:%M:%S")  
        
        if data.config.covid_ww_board_enabled:
            for case in self.worldwide_data:
                if case == "updated":
                    break              
                self.draw_count(case, self.worldwide_data[case],  self.last_update, "WW")
                self.sleepEvent.wait(5)
            

        if data.config.covid_country_board_enabled:
            for case in self.country_data:
                if case not in ("cases", "todayCases", "deaths","todayDeaths", "recovered","critical"):
                    continue
                if case == "todayDeaths":
                    self.draw_count("Today's Deaths", self.country_data[case],  self.last_update, self.country)
                    self.sleepEvent.wait(3)
                elif case == "todayCases":
                    self.draw_count("Today's Cases", self.country_data[case],  self.last_update, self.country)
                    self.sleepEvent.wait(3)
                else:
                    self.draw_count(case, self.country_data[case],  self.last_update, self.country)
                    self.sleepEvent.wait(3)

        if data.config.covid_us_state_board_enabled:
            for case in self.us_state_data:
                if case not in ("cases", "todayCases", "deaths","todayDeaths"):
                    continue
                if case == "todayDeaths":
                    self.draw_count("Today's Deaths", self.us_state_data[case],  self.last_update, self.us_state)
                    self.sleepEvent.wait(3)
                elif case == "todayCases":
                    self.draw_count("Today's Cases", self.us_state_data[case],  self.last_update, self.us_state)
                    self.sleepEvent.wait(3)
                else:
                    self.draw_count(case, self.us_state_data[case],  self.last_update, self.us_state)
                    self.sleepEvent.wait(3)           

    def draw_count(self, name, count, last_update, location):

        banner = {
            "cases":{
                "color":(255, 165, 0),
                "width": 20
            },
            "deaths":{
                "color":(255, 10, 10),
                "width": 24
            },
            "recovered":{
                "color":(0, 255, 0),
                "width": 36
            },
            "Today's Cases":{
                "color":(255, 165, 0),
                "width":48
            },
            "Today's Deaths":{
                "color":(255, 10, 10),
                "width":52
            },
            "critical":{
                "color":(255, 165, 0),
                "width": 28
            }
        }
        

        self.matrix.clear()

        self.matrix.draw.rectangle([0, 0, 30, 6], fill=(0,255,0))
        
        self.matrix.draw_text_layout(
            self.layout.board_title,
            "COVID-19".upper()
        )

        self.matrix.draw_text_layout(
            self.layout.lastupdate,
            f"{last_update} ".upper()
        )
        self.matrix.draw_text_layout(
            self.layout.count,
            str(count)
        )      
        
        loc_width = len(location) * 4
        self.matrix.draw.rectangle([loc_width, 8, banner[name]["width"] + 8 , 14], fill=banner[name]["color"])
        
        self.matrix.draw_text_layout(
            self.layout.location,
            location.upper()
        )
        
        self.matrix.draw_text_layout(
            self.layout.name,
            name.upper()
        )
        
        for i in range(30):
            self.matrix.draw_pixel((random.randrange(30, 35), random.randrange(0, 7)), (0,random.randrange(90, 255),0))

        for i in range(10):
            self.matrix.draw_pixel((random.randrange(35, 40), random.randrange(3, 7)), (0,random.randrange(30, 200),0))
        
        for i in range(5):
            self.matrix.draw_pixel((random.randrange(40, 45), random.randrange(5, 7)), (0,random.randrange(30, 160),0))
            
        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()
