import driver

if driver.is_hardware():
    from rgbmatrix import graphics
else:
    from RGBMatrixEmulator import graphics

from PIL import ImageFont, Image
from utils import center_text
import datetime
import debug
from time import sleep
from utils import get_file

class Christmas:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.font = data.config.layout.font
        self.font.large = data.config.layout.font_large_2
        self.font.scroll = data.config.layout.font_xmas
        self.days_to_xmas = 0
        self.scroll_pos = self.matrix.width

    def draw(self):
        
        debug.info("Christmas board launched")
        
        self.calc_days_to_xmas()

        #for testing purposes
        #self.days_to_xmas = 0

        debug.info(str(self.days_to_xmas) + " days to xmas")

        if self.days_to_xmas == 0:
            #today is christmas
            self.xmas_today()

        else:
            #today is not Christmas
            self.xmas_countdown()
  
    def calc_days_to_xmas(self):
        #get today's date

        today = datetime.date(
            datetime.datetime.now().year,
            datetime.datetime.now().month,            
            datetime.datetime.now().day
            )
        
        #find the next christmas
        if today.month == 12 and today.day > 25:
            xmas_year = today.year + 1
        else:
            xmas_year = today.year

        xmas = datetime.date(xmas_year,12,25)
        
        #calculate days to xmas
        self.days_to_xmas = (xmas - today).days
    
    def xmas_today(self) :
        #  it's Christmas!

        duration = 5
        i = 0
        scroll_rate = .01
            
        debug.info("It's Christmas!")

        while not self.sleepEvent.is_set():

            self.matrix.clear()

            xmas_scroll_text = self.matrix.draw_text(
                (self.scroll_pos,12),
                "MERRY CHRISTMAS!",
                font=self.font.scroll,
                fill=(0,255,0)
                )
            
            xmas_scroll_text_width = xmas_scroll_text["size"][0] + 3
            
            xmas_image = Image.open(get_file('assets/images/sleigh.png'))
            self.matrix.draw_image((self.scroll_pos + xmas_scroll_text_width,4), xmas_image)

            xmas_content_width = xmas_scroll_text_width + 48

            if(self.scroll_pos < (0 - xmas_content_width) ): self.scroll_pos = self.matrix.width

            i += scroll_rate
            self.scroll_pos -= 1

            self.matrix.render()
            #sleep(scroll_rate)
            self.sleepEvent.wait(scroll_rate)

            if(i > duration) : break

    def xmas_countdown(self) :
        
        self.matrix.clear()
        
        debug.info("Counting down to Christmas!")
        #check for three-digit countdown
        if self.days_to_xmas < 99:
            x_pos = 7
        else:
            x_pos = 1

        #draw days to xmas
        self.matrix.draw_text(
            (x_pos,6),
            str(self.days_to_xmas),
             font=self.font.large,
             fill=(0,255,0)
        )
        
        #choose one of three daily images to draw based on days to xmas and draw it
        if self.days_to_xmas % 3 == 0:
            xmas_image = Image.open(get_file('assets/images/xmas_tree.png'))
        elif self.days_to_xmas % 3 == 2:
            xmas_image = Image.open(get_file('assets/images/candy_cane.png'))
        else:
            xmas_image = Image.open(get_file('assets/images/gbread.png'))

        self.matrix.draw_image((36,1), xmas_image)
           
        #draw bottom text        
        self.matrix.draw_text(
            (1,26), 
            "DAYS TO CHRISTMAS", 
            font=self.font,
            fill=(255,0,0)
        )

        self.matrix.render()
        self.sleepEvent.wait(15)
