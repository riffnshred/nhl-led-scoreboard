from PIL import Image, ImageFont, ImageDraw, ImageSequence

from rgbmatrix import graphics

from time import sleep
from utils import center_text,get_file
import debug

class wxForecast:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        
        self.layout = self.data.config.config.layout.get_board_layout('wx_curr_temp')
        
        self.wxfont = data.config.layout.wxfont

        self.matrix = matrix

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
    
        #self.duration = data.config.weather_duration
        
        # if self.duration < 30:
        #     debug.error("Duration is less than 30 seconds, defaulting to 30 seconds")
        #     self.duration = 30

        self.duration = self.data.config.weather_forecast_days * 6
        display_wx = 0
        show_day = 0
        display_sleep = 10

        if self.data.forecast_updated or not self.data.config.weather_forecast_enabled:
            
            while show_day < self.data.config.weather_forecast_days and not self.sleepEvent.is_set():
                #Get size of summary text for looping 
                if len(self.data.wx_forecast) > 0:
                    #Testing only
                    #self.data.wx_current[2] = "Light Rainshower"
                    summary_info = self.matrix.draw_text(["1%", "77%"],self.data.wx_forecast[show_day][1],self.wxfont)
                    self.summary_width = summary_info["size"][0]
                else:
                    self.summary_width = self.matrix.width

                if self.summary_width > self.matrix.width:
                    self.summary_width += 20 #To place string off of screen, the font is width of 8 pixels
                    self.scroll_summary = True
                else:
                    self.scroll_summary = False
                self.WxDrawForecast(display_sleep,show_day)
                #display_wx += display_sleep
                show_day += 1
        else:
            if not self.data.config.weather_forecast_enabled:
                debug.error("Forecast not enabled in config.json ....")
            else:
                debug.error("Forecast feed has not updated yet....")
        
    def WxDrawForecast(self,display_loop,forecast_day=1):

        if not self.data.config.weather_forecast_enabled or not self.data.config.weather_enabled:
            debug.info("Weather forecast not enabled, skipping display of Forecast board")
            return
        
        x=0
        pos = self.matrix.width
        # If the summary is to scroll, change size of display loop
        if self.scroll_summary:
            display_loop = ((self.summary_width/self.matrix.width)/0.1)*display_loop

        while x < display_loop and not self.sleepEvent.is_set():
            self.matrix.clear()

            # Get the current weather icon
        
            curr_wx_icontext = self.data.wx_forecast[forecast_day][2]

            self.matrix.draw_text_layout(
                self.layout.condition,
                curr_wx_icontext
            )  

            if not self.scroll_summary:
                self.matrix.draw_text_layout(
                    self.layout.summary,
                    self.data.wx_forecast[forecast_day][1] 
                )
            else:
                self.matrix.draw_text([pos,"67%"],self.data.wx_forecast[forecast_day][1],self.wxfont)
                if self.summary_width > pos:
                    pos -= 1
                    if pos + self.summary_width < 0:
                        pos = self.matrix.width
                    self.sleepEvent.wait(0.1)
                
            self.matrix.draw_text_layout(
                self.layout.update,
                self.data.wx_forecast[forecast_day][0]
            )

            # High temperature for the day is red
            self.matrix.draw_text_layout(
                self.layout.forecast_temp_hi,
                self.data.wx_forecast[forecast_day][3]
            )  

            self.matrix.draw_text_layout(
                self.layout.forecast_hi,
                "H: "
            )  
        
            # Low temperature for day is blue
            self.matrix.draw_text_layout(
                self.layout.forecast_temp_lo,
                self.data.wx_forecast[forecast_day][4] 
            )

            self.matrix.draw_text_layout(
                self.layout.forecast_lo,
                "L: "
            ) 

            self.matrix.render()

            if self.data.network_issues and not self.data.config.clock_hide_indicators:
                self.matrix.network_issue_indicator()
            if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                self.matrix.update_indicator()

            if not self.scroll_summary:
                self.sleepEvent.wait(1)
            else:
                self.sleepEvent.wait(0.01)
            x+=1
    
