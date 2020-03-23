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
        self.matrix = matrix

        # Initialize
        self.wxdis_size = self.font_large.getsize(self.state)
        self.wxdis_width = self.wxdis_size[0]
        self.wxdis_align = center_text(self.wxdis_width, 28)

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        display_wx = 0
        while display_time < self.duration and not self.sleepEvent.is_set():
            display_time += 1
            #sleep(1)
            self.sleepEvent.wait(1)
        
    def dsWxDraw(self):

        self.matrix.clear()

        # Get the current weather icon
        icon_loc = 'src/weather/icons/' + self.data.wx_ds_iconset + '/' + self.data.wx_current[1] + '.png'

        curr_wx_icon = Image.open(get_file(icon_loc))


        if self.data.network_issues:
            self.matrix.network_issue_indicator()




    