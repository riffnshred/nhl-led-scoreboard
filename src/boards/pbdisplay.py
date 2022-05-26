from PIL import Image, ImageFont, ImageDraw, ImageSequence

import driver

if driver.is_hardware():
    from rgbmatrix import graphics
else:
    from RGBMatrixEmulator import graphics
from time import sleep
from utils import center_text,get_file

DISPLAY_DURATION = 5

class pbDisplay:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.font = data.config.layout.font
        #self.font_large = data.config.layout.font_large_2
        self.font_large = data.config.layout.font_pb
        self.matrix = matrix
        self.state = data.pb_state

        # Initialize
        self.pbdis_size = self.font_large.getsize(self.state)
        self.pbdis_width = self.pbdis_size[0]
        self.pbdis_align = center_text(self.pbdis_width, 28)

        self.pb_reboot_icon = Image.open(get_file('assets/images/reboot.png'))
        self.pb_halt_icon = Image.open(get_file('assets/images/halt.png'))

        display_time = 0
        while display_time < DISPLAY_DURATION:
            self.draw_pbdis()
            display_time += 1
            sleep(1)
        
    def draw_pbdis(self):
        
        self.matrix.clear()
        

        if self.state == "REBOOT":
            self.matrix.draw_image(["50%", "50%"] , self.pb_reboot_icon,"center-center")

            self.matrix.draw_text(["50%", "50%"], self.state,font=self.font_large,
                                fill=(0, 255, 0),
                                 align="center-center")

            
        else:

            self.matrix.draw_image(["50%", "50%"] , self.pb_halt_icon,"center-center")

            self.matrix.draw_text(["50%", "50%"], self.state,font=self.font_large,
                              fill=(255, 0, 0),
                              align="center-center")



        self.matrix.render()
