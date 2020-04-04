from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text,get_file

DISPLAY_DURATION = 5

class wxAlert:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.layout = self.data.config.config.layout.get_board_layout('wx_alerts')
        self.matrix = matrix

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        while not self.sleepEvent.is_set():
            self.wxDrawAlerts()
            sleep(1)
    
    def wxDrawAlerts(self):

        self.matrix.clear()

        # Draw Alert boxes and numbers (warning,watch,advisory) for 64x32 board
        #self.matrix.draw.rectangle([60, 25, 64, 32], fill=(255,0,0)) # warning
        self.matrix.draw.rectangle([0, 0, 64, 32], fill=(255,0,0)) # warning
        self.matrix.render()
        sleep(1)
        self.matrix.draw.rectangle([0, 0, 64, 32], fill=(0,0,0)) # warning
        
        """ if self.data.wx_units[5] == "us":
            self.matrix.draw.rectangle([0, 12, 64, 18], fill=(255,165,0)) # watch
            self.matrix.draw.rectangle([0, 19, 64, 25], fill=(255,255,0)) #advisory
        else:
            self.matrix.draw.rectangle([0, 12, 64, 18], fill=(255,255,0)) # watch
            self.matrix.draw.rectangle([0, 19, 64, 25], fill=(169,169,169)) #advisory """

        self.matrix.render()