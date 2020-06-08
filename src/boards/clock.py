from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
from time import sleep
from utils import center_text


class Clock:
    def __init__(self, data, matrix, sleepEvent ,duration=None):

        self.data = data
        self.date = datetime.datetime.today()
        self.time = datetime.datetime.now()
        
        self.matrix = matrix
        self.time_format = data.config.time_format
        self.duration = duration
        #Is the weather clock json loaded
        self.wx_clock = False
        
        if not self.duration:
            self.duration = data.config.clock_board_duration
        
        if self.data.config.weather_show_on_clock and self.data.wx_updated:
            self.layout = self.data.config.config.layout.get_board_layout('wx_clock')
            self.wx_clock = True
        else:
            self.layout = self.data.config.config.layout.get_board_layout('clock')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        display_time = 0
        while display_time < self.duration and not self.sleepEvent.is_set():
            self.time = datetime.datetime.now().strftime(self.time_format.replace(":", " "))
            self.meridiem = datetime.datetime.now().strftime("%P")
            display_time += 1
            self.draw_clock()
            #sleep(1)
            self.sleepEvent.wait(1)

            self.time = datetime.datetime.now().strftime(self.time_format)
            self.meridiem = datetime.datetime.now().strftime("%P")
            self.draw_clock()
            display_time += 1
            #sleep(1)
            self.sleepEvent.wait(1)

    def draw_clock(self):
        self.matrix.clear()
        
        self.matrix.draw_text_layout(
            self.layout.time,
            self.time
        )
        
        self.matrix.draw_text_layout(
            self.layout.date, 
            self.date.strftime("%b %d %Y")
        )

        if self.time_format == "%I:%M":
            self.matrix.draw_text_layout(
                self.layout.meridiem,
                "{}\n{}".format(self.meridiem[0], self.meridiem[1])
            )

        # Display curr temp and humidity on clock, bottom
        if self.data.config.weather_show_on_clock and self.wx_clock:
            self.matrix.draw_text_layout(
            self.layout.wx_display, 
            self.data.wx_current[3] + " " +self.data.wx_current[5]
            ) 
            if len(self.data.wx_alerts) > 0:
                # Draw Alert box (warning,watch,advisory)
                #self.matrix.draw.rectangle([60, 25, self.matrix.width, 32], fill=(255,0,0)) # warning
                if self.data.wx_alerts[1] == "warning":  
                    self.matrix.draw.rectangle([57, 25, self.matrix.width, 32], fill=(255,0,0)) # warning
                elif self.data.wx_alerts[1] == "watch":
                    if self.data.wx_units[5] == "us":
                        self.matrix.draw.rectangle([57, 25, self.matrix.width, 32], fill=(255,165,0)) # watch
                    else:
                        self.matrix.draw.rectangle([57, 25, self.matrix.width, 32], fill=(255,255,0)) # watch canada
                else:
                    if self.data.wx_alerts[1] == "advisory":
                        if self.data.wx_units[5] == "us":
                            self.matrix.draw.rectangle([57, 25, self.matrix.width, 32], fill=(255,255,0)) #advisory
                        else:
                            self.matrix.draw.rectangle([57, 25, self.matrix.width, 32], fill=(169,169,169)) #advisory canada

        self.matrix.render()
        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()

        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()
