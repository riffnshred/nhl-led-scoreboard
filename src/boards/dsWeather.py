from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text,get_file
import debug

class dsWeather:
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

        # DarkSky weather icons for top left of board using the weatherfot.ttf
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
                        "tornado": '\uf056',
                        None: '\uf07b'
        }

        display_wx = 0
        display_sleep = self.duration/3
        while display_wx < self.duration and not self.sleepEvent.is_set():
            self.dsWxDrawTemp()
            self.sleepEvent.wait(display_sleep)
            display_wx += display_sleep
            self.dsWxDrawWind()
            self.sleepEvent.wait(display_sleep)
            display_wx += display_sleep
            self.dsWxDrawPrecip()
            self.sleepEvent.wait(display_sleep)
            display_wx += display_sleep
        
    def dsWxDrawTemp(self):

        self.matrix.clear()

        # Get the current weather icon
    
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


        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()
    
    def dsWxDrawWind(self):
        
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

    def dsWxDrawPrecip(self):
        
        self.matrix.clear()

        precip_wx_icon = self.wx_cond[self.data.wx_curr_precip[0]]

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

        self.matrix.draw_text_layout(
             self.layout3.humidity,
              self.data.wx_current[5] + " Humidity"
        )
    
        if len(self.data.wx_alerts) > 0:
            # Draw Alert boxes and numbers (warning,watch,advisory) for 64x32 board
            #self.matrix.draw.rectangle([60, 25, 64, 32], fill=(255,0,0)) # warning
            self.matrix.draw.rectangle([58, 5, 64, 11], fill=(255,0,0)) # warning

            if self.data.wx_units[5] == "us":
                self.matrix.draw.rectangle([58, 12, 64, 18], fill=(255,165,0)) # watch
                self.matrix.draw.rectangle([58, 19, 64, 25], fill=(255,255,0)) #advisory
            else:
                self.matrix.draw.rectangle([58, 12, 64, 18], fill=(255,255,0)) # watch
                self.matrix.draw.rectangle([58, 19, 64, 25], fill=(169,169,169)) #advisory

        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()


    