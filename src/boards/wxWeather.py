from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text,get_file
import debug

class wxWeather:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        
        self.layout = self.data.config.config.layout.get_board_layout('wx_curr_temp')
        self.layout2 = self.data.config.config.layout.get_board_layout('wx_curr_wind')
        self.layout3 = self.data.config.config.layout.get_board_layout('wx_curr_precip')

        self.matrix = matrix

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        self.duration = data.config.weather_duration
        if self.duration < 30:
            debug.error("Duration is less than 30 seconds, defaulting to 30 seconds")
            self.duration = 30


        display_wx = 0
        display_sleep = self.duration/3
        if self.data.wx_updated:
            while display_wx < self.duration and not self.sleepEvent.is_set():
                self.WxDrawTemp()
                self.sleepEvent.wait(display_sleep)
                display_wx += display_sleep
                self.WxDrawWind()
                self.sleepEvent.wait(display_sleep)
                display_wx += display_sleep
                self.WxDrawPrecip()
                self.sleepEvent.wait(display_sleep)
                display_wx += display_sleep
        else:
            debug.error("Weather feed has not updated yet....")
        
    def WxDrawTemp(self):

        self.matrix.clear()

        # Get the current weather icon
    
        curr_wx_icontext = self.data.wx_current[1]

        self.matrix.draw_text_layout(
            self.layout.condition,
            curr_wx_icontext
        )  

        self.matrix.draw_text_layout(
            self.layout.summary,
            self.data.wx_current[2] 
        )

        self.matrix.draw_text_layout(
            self.layout.update,
            self.data.wx_current[0]
        )

        self.matrix.draw_text_layout(
            self.layout.temp,
            self.data.wx_current[3]
        )  

        self.matrix.draw_text_layout(
            self.layout.temp_app,
            self.data.wx_current[4] 
        )


        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()
    
    def WxDrawWind(self):
        
        self.matrix.clear()

       #wind_wx_diricon = u'\uf05b'
        self.matrix.draw_text_layout(
            self.layout2.condition,
            #wind_wx_diricon
            self.data.wx_curr_wind[2]
        )  

        self.matrix.draw_text_layout(
            self.layout2.wind,
            self.data.wx_curr_wind[1] + " @ " + self.data.wx_curr_wind[0]
        )  

        self.matrix.draw_text_layout(
            self.layout2.gust,
            "Gusts to:\n" + self.data.wx_curr_wind[3]
        )  

        self.matrix.draw_text_layout(
            self.layout2.pressure,
            self.data.wx_curr_wind[4]
        )  

        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()

    def WxDrawPrecip(self):
        
        self.matrix.clear()

        precip_wx_icon = '\uf07b' #N/A

        if self.data.config.weather_data_feed.lower() == "ds":
            if self.data.wx_curr_precip[0] == None:
                wx_curr_precip = "N/A"
                self.matrix.draw_text_layout(
                    self.layout3.preciptype_na,
                    precip_wx_icon
                )
            else:
                wx_curr_precip = self.data.wx_curr_precip[0]
                self.matrix.draw_text_layout(
                    self.layout3.preciptype,
                    precip_wx_icon
                )  
                
            self.matrix.draw_text_layout(
                self.layout3.precipchance,
                "Chance: " + wx_curr_precip + "\n" + self.data.wx_curr_precip[1]
            ) 
        
        #if self.data.config.weather_data_feed.lower() == "ec":


        self.matrix.draw_text_layout(
             self.layout3.humidity,
              self.data.wx_current[5] + " Humidity"
        )
    
        if len(self.data.wx_alerts) > 0:
            # Draw Alert boxes (warning,watch,advisory) for 64x32 board
            # Only draw the highest 
            #self.matrix.draw.rectangle([60, 25, 64, 32], fill=(255,0,0)) # warning
            if self.data.wx_alerts[1] == "warning": 
                self.matrix.draw.rectangle([58, 10, 64, 20], fill=(255,0,0)) # warning
            elif self.data.wx_alerts[1] == "watch":
                if self.data.wx_units[5] == "us":
                    self.matrix.draw.rectangle([58, 10, 64, 20], fill=(255,165,0)) # watch
                else:
                    self.matrix.draw.rectangle([58, 10, 64, 20], fill=(255,255,0)) # watch canada
            else:
                if self.data.wx_alerts[1] == "advisory":
                    if self.data.wx_units[5] == "us":
                        self.matrix.draw.rectangle([58, 10, 64, 20], fill=(255,255,0)) #advisory
                    else:
                        self.matrix.draw.rectangle([58, 10, 64, 20], fill=(169,169,169)) #advisory canada

        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()


    