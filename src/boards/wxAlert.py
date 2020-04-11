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
        self.pos = self.matrix.width
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.wxfont = data.config.layout.wxalert_font
        #self.data.wx_alerts = ["Severe Thunderstorm","warning","04/11 13:47"]
        #Get size of summary text for looping 
        alert_info = self.matrix.draw_text(["50%", "50%"],self.data.wx_alerts[0],self.wxfont)
        self.alert_width = alert_info["size"][0]

        #while not self.sleepEvent.is_set():
        #while True:
        self.wxDrawAlerts()
            #sleep(0.01)
    
    def wxDrawAlerts(self):

        while True:
            self.matrix.clear()
            #offscreen_canvas = self.matrix.CreateFrameCanvas()

            # Draw Alert boxes and numbers (warning,watch,advisory) for 64x32 board
            #self.matrix.draw.rectangle([60, 25, 64, 32], fill=(255,0,0)) # warning
            if self.data.wx_alerts[1] == "warning":
                self.matrix.draw.rectangle([0, 0, 64, 8], fill=(255,0,0)) # warning
                self.matrix.draw.rectangle([0, 24, 64, 32], fill=(255,0,0)) # warning
            elif self.data.wx_alerts[1] == "watch":
                if self.data.wx_units[5] == "us":
                    self.matrix.draw.rectangle([0, 0, 64, 8], fill=(255,165,0)) # watch
                    self.matrix.draw.rectangle([0, 24, 64, 32], fill=(255,165,0)) # watch
                else:
                    self.matrix.draw.rectangle([0, 0, 64, 8], fill=(255,255,0)) # watch canada
                    self.matrix.draw.rectangle([0, 24, 64, 32], fill=(255,255,0)) # watch canada
            else:
                if self.data.wx_alerts[1] == "advisory":
                    if self.data.wx_units[5] == "us":
                        self.matrix.draw.rectangle([0, 0, 64,8], fill=(255,255,0)) #advisory
                        self.matrix.draw.rectangle([0, 24, 64, 32], fill=(255,255,0)) #advisory
                    else:
                        self.matrix.draw.rectangle([0, 0, 64, 8], fill=(169,169,169)) #advisory canada
                        self.matrix.draw.rectangle([0, 24, 64, 32], fill=(169,169,169)) #advisory canada
        
            
            self.matrix.draw_text([self.pos,9],self.data.wx_alerts[0],self.wxfont,fill=(255,255,255))
            

            if self.alert_width > self.pos:
                self.pos -= 1
                if self.pos + self.alert_width == 0:
                    break
            self.matrix.render()
            