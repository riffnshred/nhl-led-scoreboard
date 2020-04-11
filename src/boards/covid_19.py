from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from datetime import datetime, timedelta
from utils import convert_time
import random

class Covid_19:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        try:
            self.data.covid19.get_all()
            self.data.network_issues = False
        except ValueError as e:
            print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
            self.data.network_issues = True

        self.worldwide_data = self.data.covid19.all
        self.layout = self.data.config.config.layout.get_board_layout('covid_19')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.last_update = convert_time((datetime(1970, 1, 1) + timedelta(milliseconds=self.worldwide_data['updated'])).strftime("%Y-%m-%dT%H:%M:%SZ")).strftime("%m/%d %H:%M:%S")
        for case in self.worldwide_data:
            if case == "cases" or case == "deaths" or case == "recovered" :
                print(case)
                self.draw_count(case, self.worldwide_data[case],  self.last_update)
                self.sleepEvent.wait(5)
                

    def draw_count(self, name, count, last_update):

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
        self.matrix.draw.rectangle([8, 8, banner[name]["width"] + 8 , 14], fill=banner[name]["color"])
        
        self.matrix.draw_text_layout(
            self.layout.location,
            "WW".upper()
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