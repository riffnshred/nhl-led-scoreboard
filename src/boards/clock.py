from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime
from time import sleep
from utils import center_text


class Clock:
    def __init__(self, data, matrix, sleepEvent,duration=None):
        self.data = data
        self.date = datetime.datetime.today()
        self.time = datetime.datetime.now()
        self.font = data.config.layout.font
        self.font_large = data.config.layout.font_large_2
        self.matrix = matrix
        self.time_format = data.config.time_format
        self.duration = duration
        if not self.duration:
            self.duration = data.config.clock_board_duration
        
        self.layout = self.data.config.config.layout.get_board_layout('clock')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        # Initialize the clock
        self.clock_size = self.font_large.getsize(self.time.strftime(self.time_format))
        self.clock_width = self.clock_size[0]
        self.time_align = center_text(self.clock_width, 32)

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
        self.clock_size = self.font_large.getsize(self.time)
        self.clock_width = self.clock_size[0]
        self.time_align = center_text(self.clock_width, 32)
        self.matrix.clear()

        # self.matrix.draw_text((self.time_align, 4), "{}".format(self.date.strftime("%b %d %Y")),
        #                       fill=(255, 255, 255),
        #                       font=self.font, multiline=True)

        # self.matrix.draw_text((self.time_align, 9), "{}".format(self.time),
        #                       fill=(255, 50, 50),
        #                       font=self.font_large, multiline=True)

        # # If time format is 12h, show the meridiem
        # if self.time_format == "%I:%M":
        #     h = 11
        #     for letter in self.meridiem:
        #         self.matrix.draw_text((self.time_align + (self.clock_width - 2), h), "{}".format(letter),
        #                               fill=(255, 255, 255),
        #                               font=self.font, multiline=True)
        #         h += 6

        self.matrix.draw_text_layout(
            self.layout.date, 
            self.date.strftime("%b %d %Y"),
            fill=(255, 255, 255),
            font=self.font, 
            multiline=True
        )

        self.matrix.draw_text_layout(
            self.layout.time,
            self.time,
            fill=(255, 50, 50),
            font=self.font_large,
            multiline=True
        )

        self.matrix.draw_text_layout(
            self.layout.meridiem,
            "{}\n{}".format(self.meridiem[0], self.meridiem[1]),
            fill=(255, 255, 255),
            font=self.font,
            multiline=True
        )

        # # If time format is 12h, show the meridiem
        # if self.time_format == "%I:%M":
        #     h = 11
        #     for letter in self.meridiem:
        #         self.matrix.draw_text_layout((self.time_align + (self.clock_width - 2), h), "{}".format(letter),
        #                               fill=(255, 255, 255),
        #                               font=self.font, multiline=True)
        #         h += 6

        self.matrix.render()
        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()
