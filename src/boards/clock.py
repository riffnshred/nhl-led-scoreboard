from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
import re
import debug
from time import sleep
from utils import center_text
import traceback

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

        #Get team colors to use for the clock
        self.team_colors = data.config.team_colors
        self.preferred_teams = data.pref_teams


        #Select the first preferred team for clock setting
        self.clock_color = self.team_colors.color("{}.primary".format(self.preferred_teams[0]))
        self.wxdt_color = self.team_colors.color("{}.text".format(self.preferred_teams[0]))

        #If text of team is black, force to white
        if self.wxdt_color == {'r': 0, 'b': 0, 'g': 0}:
            self.wxdt_color = {'r': 255, 'b': 255, 'g': 255}

        r = r"(\d+),\s*(\d+),\s*(\d+)"

        if self.data.config.clock_team_colors:
            self.clockfill = (self.clock_color['r'],self.clock_color['g'],self.clock_color['b'])
            self.wxdtfill = (self.wxdt_color['r'],self.wxdt_color['g'],self.wxdt_color['b'])
        elif len(self.data.config.clock_clock_rgb) > 0 or len(self.data.config.clock_date_rgb) > 0:
            if len(self.data.config.clock_clock_rgb) > 0:
                #Test string to make sure it's in rgb format
                if re.match(r,self.data.config.clock_clock_rgb) is not None:
                    if all(0 <= int(group) <= 255 for group in re.match(r, self.data.config.clock_clock_rgb).groups()):
                        self.clockfill = eval(self.data.config.clock_clock_rgb)
                    else:
                        debug.error("Invalid RGB values for clock_rgb {}, falling back to default".format(self.data.config.clock_clock_rgb))
                        self.clockfill = None
                else:
                    debug.error("clock_rgb {} is not a valid RGB tuple (r,g,b), falling back to default".format(self.data.config.clock_clock_rgb))
                    self.clockfill = None
            else:
                self.clockfill = None

            if len(self.data.config.clock_date_rgb) > 0:
                if re.match(r,self.data.config.clock_date_rgb) is not None:
                    if all(0 <= int(group) <= 255 for group in re.match(r, self.data.config.clock_date_rgb).groups()):
                        self.wxdtfill = eval(self.data.config.clock_date_rgb)
                    else:
                        debug.error("Invalid RGB values for date_rgb {}, falling back to default".format(self.data.config.clock_date_rgb))
                        self.wxdtfill = None
                else:
                    debug.error("date_rgb {} is not a valid RGB tuple (r,g,b), falling back to default".format(self.data.config.clock_date_rgb))
                    self.wxdtfill = None
            else:
                self.wxdtfill = None
        else:
            self.clockfill = None
            self.wxdtfill = None

        #Force to original layout.color if text is set to black for clock or weather/date text
        if self.wxdtfill == {'r': 0, 'b': 0, 'g': 0}:
            self.wxdtfill = None

        if self.clockfill == {'r': 0, 'b': 0, 'g': 0}:
            self.clockfill = None

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
            if self.data.config.clock_flash_seconds:
                self.time = datetime.datetime.now().strftime(self.time_format.replace(":", " "))
            else:
                self.time = datetime.datetime.now().strftime(self.time_format)
            self.meridiem = datetime.datetime.now().strftime("%P")
            display_time += 1
            self.draw_clock()
            #sleep(1)
            self.sleepEvent.wait(1)
            if self.data.config.clock_flash_seconds:
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
            self.time,
            fillColor=self.clockfill
        )

        self.matrix.draw_text_layout(
            self.layout.date,
            self.date.strftime("%b %d %Y").upper(),
            fillColor=self.wxdtfill
        )

        if self.time_format == "%I:%M":
            self.matrix.draw_text_layout(
                self.layout.meridiem,
                "{}\n{}".format(self.meridiem[0], self.meridiem[1]),
                fillColor=self.wxdtfill
            )

        # Display curr temp and humidity on clock, bottom
        if self.data.config.weather_show_on_clock and self.wx_clock:
            self.matrix.draw_text_layout(
            self.layout.wx_display,
            self.data.wx_current[3] + " " +self.data.wx_current[5],
            fillColor=self.wxdtfill
            )
            if len(self.data.wx_alerts) > 0 and self.data.config.wxalert_show_on_clock:
                # Draw Alert box (warning,watch,advisory)
                #self.matrix.draw.rectangle([60, 25, self.matrix.width, 32], fill=(255,0,0)) # warning
                if self.data.wx_alerts[1] == "warning":
                    if self.data.config.wxalert_alert_feed.lower() == "nws":
                        self.matrix.draw.rectangle([self.matrix.width -7, self.matrix.height -7 , self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) # warning
                    else:
                        self.matrix.draw.rectangle([self.matrix.width -7, self.matrix.height -7 , self.matrix.width, self.matrix.height], fill=(255,0,0)) # warning
                elif self.data.wx_alerts[1] == "watch":
                    if self.data.config.wxalert_alert_feed.lower() == "nws":
                        self.matrix.draw.rectangle([self.matrix.width - 7, self.matrix.height -7 , self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) # watch
                    else:
                        self.matrix.draw.rectangle([self.matrix.width - 7, self.matrix.height - 7, self.matrix.width, self.matrix.height], fill=(255,255,0)) # watch canada
                else:
                    if self.data.wx_alerts[1] == "advisory":
                        if self.data.config.wxalert_alert_feed.lower() == "nws":
                            self.matrix.draw.rectangle([self.matrix.width - 7, self.matrix.height - 7 , self.matrix.width, self.matrix.height], fill=self.data.wx_alerts[5]) #advisory
                        else:
                            self.matrix.draw.rectangle([self.matrix.width - 7, self.matrix.height - 7, self.matrix.width, self.matrix.height], fill=(169,169,169)) #advisory canada

        self.matrix.render()
        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()

        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()
