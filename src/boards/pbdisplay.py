from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text

DISPLAY_DURATION = 5

class pbDisplay:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.font = data.config.layout.font
        #self.font_large = data.config.layout.font_large_2
        self.font_large = data.config.layout.font_pb
        self.matrix = matrix
        self.state = data.pb_state

        # Initialize the REBOOTING
        self.pbdis_size = self.font_large.getsize(self.state)
        self.pbdis_width = self.pbdis_size[0]
        self.pbdis_align = center_text(self.pbdis_width, 28)

        display_time = 0
        while display_time < DISPLAY_DURATION:
            self.draw_pbdis()
            display_time += 1
            sleep(1)
        
    def draw_pbdis(self):
        
        self.matrix.clear()
        if self.state == "REBOOT":
            self.matrix.draw_text((self.pbdis_align, 8), self.state,
                                fill=(255, 255, 0),
                                font=self.font_large, multiline=False,location="center")
        else:
            self.matrix.draw_text((self.pbdis_align, 8), self.state,
                              fill=(255, 0, 0),
                              font=self.font_large, multiline=False,location="center")


        self.matrix.render()
