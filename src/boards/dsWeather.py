from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text,get_file

class dsWeather:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.font = data.config.layout.font
        #self.font_large = data.config.layout.font_large_2
        self.font_large = data.config.layout.font_pb
        self.layout = self.data.config.config.layout.get_board_layout('wx_curr_1')
        self.layout2 = self.data.config.config.layout.get_board_layout('wx_curr_2')
        self.matrix = matrix


        # Initialize
        # self.wxdis_size = self.font_large.getsize(self.state)
        # self.wxdis_width = self.wxdis_size[0]
        # self.wxdis_align = center_text(self.wxdis_width, 28)

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        self.duration = data.config.weather_duration

        # DarkSky weather icons for top left of board
        self.wx_cond = {"clear-day": '\uf00d',
                        "clear-night": '\uf02e',
                        "partly-cloudy-night": '\uf031',
                        "partly-cloudy-day": '\uf002',
                        "rain": '\uf019',
                        "snow": '\uf01b',
                        "sleet": '\uf0b5',
                        "wind": '\uf050',
                        "fog": '\uf014',
                        "cloudy": '\uf013',
                        "hail": '\uf015',
                        "thunderstorm": '\uf01e',
                        "tornado": '\uf056'
        }

        display_wx = 0
        while display_wx < self.duration and not self.sleepEvent.is_set():
            display_wx += 1
            self.dsWxDrawPg1()
            sleep(4)
            self.dsWxDrawPg2()
            sleep(4)
            self.sleepEvent.wait(1)
        
    def dsWxDrawPg1(self):

        self.matrix.clear()

        # Get the current weather icon
        
        #self.matrix.draw_image([42, -3] , curr_wx_icon,"top-right")
        #self.matrix.draw_image(["67%","-9%"] , curr_wx_icon,"top-right")
        #curr_wx_icontext = u'\uf00d'
        curr_wx_icontext = self.wx_cond[self.data.wx_current[1]]

        self.matrix.draw_text_layout(
            self.layout.condition,
            curr_wx_icontext
        )  

        self.matrix.draw_text_layout(
            self.layout.summary,
            self.data.wx_current[2] + "\n" +self.data.wx_current[0]
        )

        self.matrix.draw_text_layout(
            self.layout.temp,
            self.data.wx_current[3]
        )  

        self.matrix.draw_text_layout(
            self.layout.temp_app,
            self.data.wx_current[4] 
        )

        self.matrix.draw_text_layout(
            self.layout.humidity,
            self.data.wx_current[5] + " Hum"
        )

        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()
    
    def dsWxDrawPg2(self):
        
        self.matrix.clear()

        wind_wx_diricon = u'\uf05b'
        self.matrix.draw_text_layout(
            self.layout2.condition,
            wind_wx_diricon
        )  

        self.matrix.draw_text_layout(
            self.layout2.wind,
            + self.data.wx_curr_wind[1] + " @ "+ self.data.wx_curr_wind[0]
        )  

        self.matrix.draw_text_layout(
            self.layout2.gust,
            "Gusts\n" + self.data.wx_curr_wind[2]
        )  

        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()




    