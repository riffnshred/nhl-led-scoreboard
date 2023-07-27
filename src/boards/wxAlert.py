from PIL import Image, ImageFont, ImageDraw, ImageSequence

import driver

if driver.is_hardware():
    from rgbmatrix import graphics
else:
    from RGBMatrixEmulator import graphics

from time import sleep
from utils import center_text,get_file
import debug

class wxAlert:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.layout4 = self.data.config.config.layout.get_board_layout('wx_alert')
        self.matrix = matrix
        self.pos = self.matrix.width
        self.sleepEvent = sleepEvent
        self.scroll = self.data.config.wxalert_scroll_alert

        if self.sleepEvent.is_set():
            self.sleepEvent.clear()
        else:
            self.scroll = False
        
        self.wxfont = data.config.layout.wxalert_font

        #Make sure there's an alert active before showing. 
        #Check so wxalert can be used as a standalone board

        if len(self.data.wx_alerts) > 0:
            #Get size of summary text for looping 
            alert_info = self.matrix.draw_text(["50%", "50%"],self.data.wx_alerts[0],self.wxfont)
            #Set the width, add 3 to allow for text to scroll completely off screen
            self.alert_width = alert_info["size"][0] + 3

            if self.alert_width < self.pos:
                self.alert_width = self.pos + 1

            

            if not self.scroll:
                # Force to display the top and bottom titles on static display
                # This will be similar to the weather board alert display
                self.drawtitle = True
            else:
                self.drawtitle = self.data.config.wxalert_alert_title
            
            self.duration = self.data.config.wxalert_alert_duration
            
            
            self.wxDrawAlerts()
        else:
            if self.data.config.wxalert_show_alerts:
                debug.info("No active weather alerts in your area, wxalert board not displayed")
            else:
                debug.error("wxalert board not enabled in config.json.  Is show_alerts set to True?")
    
    def wxDrawAlerts(self):

        i = 0
        while True:
            self.matrix.clear()
            #offscreen_canvas = self.matrix.CreateFrameCanvas()

            if self.data.config.wxalert_alert_feed.lower() == "nws":
                top_title = self.data.wx_alerts[4]
            else:
                top_title = "Weather"

            if self.drawtitle:
                if self.data.wx_alerts[0] == "Severe Thunderstorm":
                    self.data.wx_alerts[0] = "Svr T-Storm"
                if self.data.wx_alerts[0] == "Freezing Rain":
                    self.data.wx_alerts[0] = "Frzn Rain"
                if self.data.wx_alerts[0] == "Freezing Drizzle":
                    self.data.wx_alerts[0] = "Frzn Drzl"

            # Draw Alert boxes and numbers (warning,watch,advisory) for 64x32 board
            #self.matrix.draw.rectangle([60, 25, 64, 32], fill=(255,0,0)) # warning
            if self.data.wx_alerts[1] == "warning":
                if self.data.config.wxalert_alert_feed.lower() == "nws":
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=self.data.wx_alerts[5]) # warning
                    self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) # warning    
                else:
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,0,0)) # warning
                    self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=(255,0,0)) # warning
                
                if self.drawtitle:     
                    self.matrix.draw_text_layout(
                        self.layout4.title_top,
                        top_title
                    )  
                    self.matrix.draw_text_layout(
                        self.layout4.title_bottom,
                        "Warning"
                    )  

            elif self.data.wx_alerts[1] == "watch":
                if self.data.config.wxalert_alert_feed.lower() == "nws":
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=self.data.wx_alerts[5]) # watch
                    self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) # watch
                else:
                    self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(255,255,0)) # watch canada
                    self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=(255,255,0)) # watch canada
                if self.drawtitle:   
                    self.matrix.draw_text_layout(
                        self.layout4.title_top,
                        top_title
                    )  
                    self.matrix.draw_text_layout(
                        self.layout4.title_bottom,
                        "Watch"
                    )  
            else:
                if self.data.wx_alerts[1] == "advisory":
                    if self.data.config.wxalert_alert_feed.lower() == "nws":
                        self.matrix.draw.rectangle([0, 0, self.matrix.width,8], fill=self.data.wx_alerts[5]) #advisory
                        self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) #advisory
                    else:
                        self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(169,169,169)) #advisory canada
                        self.matrix.draw.rectangle([0, self.matrix.height - 8, self.matrix.width, self.matrix.height], fill=(169,169,169)) #advisory canada
                    
                    if self.drawtitle:
                        self.matrix.draw_text_layout(
                            self.layout4.title_top,
                            top_title
                        )  
                        self.matrix.draw_text_layout(
                            self.layout4.title_bottom,
                            "Advisory"
                        )  

            if self.scroll:
                self.matrix.draw_text([self.pos,9],self.data.wx_alerts[0],self.wxfont,fill=(255,255,255))
                

                if self.alert_width > self.pos:
                    self.pos -= 1
                    if self.pos + self.alert_width == 0:
                        break
                self.matrix.render()
                sleep(0.1)
            else:
                self.matrix.draw_text_layout(
                    self.layout4.warning,
                    self.data.wx_alerts[0]
                )
                self.matrix.draw_text_layout(
                    self.layout4.warning_date,
                    self.data.wx_alerts[2]
                )
                self.matrix.render()
                sleep(1)
                i+=1
                if i==self.duration:
                    break
            
            #Make sure that the next alert will interrrupt
            
            self.data.wx_alert_interrupt = False
            if self.data.network_issues and not self.data.config.clock_hide_indicators:
                self.matrix.network_issue_indicator()
            
            if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                self.matrix.update_indicator()
            
