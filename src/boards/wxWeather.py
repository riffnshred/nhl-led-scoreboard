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
        self.layout4 = self.data.config.config.layout.get_board_layout('wx_alert')

        self.wxfont = data.config.layout.wxfont

        self.view = data.config.weather_view
        
        # Default to full if invalid values set in config
        if self.view.lower() not in ("full", "summary"):
            debug.info("Valid value for view not found, setting to full")
            self.view = "full"

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
            #Get size of summary text for looping 
            if len(self.data.wx_current) > 0:
                #Testing only
                #self.data.wx_current[2] = "Light Rainshower"
                summary_info = self.matrix.draw_text(["1%", "77%"],self.data.wx_current[2],self.wxfont)
                self.summary_width = summary_info["size"][0]
            else:
                self.summary_width = self.matrix.width

            if self.summary_width > self.matrix.width:
                self.summary_width += 20 #To place string off of screen, the font is width of 8 pixels
                self.scroll_summary = True
            else:
                self.scroll_summary = False

            while display_wx < self.duration and not self.sleepEvent.is_set():
                self.WxDrawTemp(display_sleep)
                #self.sleepEvent.wait(display_sleep)
                display_wx += display_sleep
                if self.view.lower() == "full":
                    self.WxDrawWind()
                    self.sleepEvent.wait(display_sleep)
                    display_wx += display_sleep
                    self.WxDrawPrecip_EC()
                    self.sleepEvent.wait(display_sleep)

                # Alerts now are on their own selectable board, wxalert
                #if len(self.data.wx_alerts) > 0:
                #    if self.data.wx_alerts[1]!="ended":
                #        self.WxDrawAlert()
                #        self.sleepEvent.wait(display_sleep)

                display_wx += display_sleep
        else:
            if self.data.config.weather_enabled:
                debug.error("Weather feed (current conditions) has not updated yet....")
            else:
                debug.error("Weather board not enabled in config.json.  Is enabled set to True?")
        
    def WxDrawTemp(self,display_loop):

        x=0
        pos = self.matrix.width
        # If the summary is to scroll, change size of display loop
        if self.scroll_summary:
            display_loop = ((self.summary_width/self.matrix.width)/0.1)*display_loop

        while x < display_loop and not self.sleepEvent.is_set():
            self.matrix.clear()

            # Get the current weather icon
        
            curr_wx_icontext = self.data.wx_current[1]

            self.matrix.draw_text_layout(
                self.layout.condition,
                curr_wx_icontext
            )  

            if not self.scroll_summary:
                self.matrix.draw_text_layout(
                    self.layout.summary,
                    self.data.wx_current[2] 
                )
            else:
                self.matrix.draw_text([pos,"67%"],self.data.wx_current[2],self.wxfont)
                if self.summary_width > pos:
                    pos -= 1
                    if pos + self.summary_width < 0:
                        pos = self.matrix.width
                    self.sleepEvent.wait(0.1)
                


            self.matrix.draw_text_layout(
                self.layout.update,
                self.data.wx_current[0]
            )

            self.matrix.draw_text_layout(
                self.layout.temp,
                self.data.wx_current[3]
            )  

            # Covert temp and apparent temp to floats to compare
            if  self.data.wx_current[3] == "N/A" or self.data.wx_current[4] == "N/A":
                self.matrix.draw_text_layout(
                        self.layout.temp_app,
                        self.data.wx_current[4] 
                    )
            else:
                temp_float = float(self.data.wx_current[3][:-1])
                app_temp_float = float(self.data.wx_current[4][:-1])

                if (temp_float > app_temp_float):
                    # apparent temperature is colder than temperature, show blue
                    self.matrix.draw_text_layout(
                        self.layout.temp_app_lo,
                        self.data.wx_current[4] 
                    )
                elif (temp_float < app_temp_float):
                    # apparent temperature is warmer than temperature, show red
                    self.matrix.draw_text_layout(
                        self.layout.temp_app_hi,
                        self.data.wx_current[4] 
                    )
                else:
                    # apparent temperature is colder than temperature, show green, same as temp
                    self.matrix.draw_text_layout(
                        self.layout.temp_app,
                        self.data.wx_current[4] 
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
            self.layout2.visibility,
            "Vis: " + self.data.wx_curr_wind[6]
        )
        

        self.matrix.render()

        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()

        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()
    
    def WxDrawPrecip_EC(self):

        self.matrix.clear()

        precip_wx_icon = '\uf07b' #N/A

        self.matrix.draw_text_layout(
            self.layout3.pressure,
            self.data.wx_curr_wind[4]
        )

        if self.data.config.weather_data_feed.lower() == "ec":
            self.matrix.draw_text_layout(
                self.layout3.tendency,
                self.data.wx_curr_wind[5]
            )

        self.matrix.draw_text_layout(
            self.layout3.dewpoint,
            "Dew Pt. " + self.data.wx_current[6]
        )

        self.matrix.draw_text_layout(
            self.layout3.humidity,
            self.data.wx_current[5] + " Humidity"
        )

        self.matrix.render()

        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()

        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()
    
    def WxDrawAlert(self):
        
        self.matrix.clear()
        if self.data.wx_alerts[0] == "Severe Thunderstorm":
            self.data.wx_alerts[0] = "Svr T-Storm"
        if self.data.wx_alerts[0] == "Freezing Rain":
            self.data.wx_alerts[0] = "Frzn Rain"
        if self.data.wx_alerts[0] == "Freezing Drizzle":
            self.data.wx_alerts[0] = "Frzn Drzl"

        if self.data.wx_alerts[1] == "warning": 
            self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,0,0)) # warning

            self.matrix.draw_text_layout(
                self.layout4.warning,
                self.data.wx_alerts[0]
            )  
            self.matrix.draw_text_layout(
                self.layout4.warning_date,
                self.data.wx_alerts[2]
            )
            self.matrix.draw.rectangle([0, 24, self.matrix.width, 32], fill=(255,0,0)) # warning
            self.matrix.draw_text_layout(
                self.layout4.title_top,
                "Weather"
            )  
            self.matrix.draw_text_layout(
                self.layout4.title_bottom,
                "Warning"
            )  
        elif self.data.wx_alerts[1] == "watch":
            if self.data.wx_units[5] == "us":
                self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,165,0)) # watch
                self.matrix.draw_text_layout(
                    self.layout4.warning,
                    self.data.wx_alerts[0]
                )
                self.matrix.draw_text_layout(
                    self.layout4.warning_date,
                    self.data.wx_alerts[2]
                )
                self.matrix.draw.rectangle([0, 24, self.matrix.width, 32], fill=(255,165,0)) # watch
            else:
                self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,255,0)) # watch canada
                self.matrix.draw_text_layout(
                    self.layout4.warning,
                    self.data.wx_alerts[0]
                )
                self.matrix.draw_text_layout(
                    self.layout4.warning_date,
                    self.data.wx_alerts[2]
                )
                self.matrix.draw.rectangle([0, 24, self.matrix.width, 32], fill=(255,255,0)) # watch canada
            self.matrix.draw_text_layout(
                self.layout4.title_top,
                "Weather"
            )  
            self.matrix.draw_text_layout(
                self.layout4.title_bottom,
                "Watch"
            )  
        else:
            if self.data.wx_alerts[1] == "advisory":
                if self.data.wx_units[5] == "us":
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,255,0)) #advisory
                    self.matrix.draw_text_layout(
                        self.layout4.advisory_us,
                        self.data.wx_alerts[0]
                    )
                    self.matrix.draw_text_layout(
                        self.layout4.warning_date,
                        self.data.wx_alerts[2]
                    )
                    self.matrix.draw.rectangle([0, 24, self.matrix.width, 32], fill=(255,255,0)) #advisory
                else:
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(169,169,169)) #advisory canada
                    self.matrix.draw_text_layout(
                        self.layout4.advisory_ca,
                        self.data.wx_alerts[0]
                    )
                    self.matrix.draw_text_layout(
                        self.layout4.warning_date,
                        self.data.wx_alerts[2]
                    )
                    self.matrix.draw.rectangle([0, 24, self.matrix.width, 32], fill=(169,169,169)) #advisory canada
            self.matrix.draw_text_layout(
                self.layout4.title_top,
                "Weather"
            )  
            self.matrix.draw_text_layout(
                self.layout4.title_bottom,
                "Advisory"
            )  

        self.matrix.render()

        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()

        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()
