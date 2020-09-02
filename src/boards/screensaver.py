from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
from utils import center_text,get_file

DISPLAY_DURATION = 5

class screenSaver:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.status = self.data.status
        self.font = data.config.layout.font   
        self.matrix = matrix
        


        self.toaster = Image.open(get_file('assets/animations/screensaver/spectrum.gif'))

        display_time = 0
        while display_time < DISPLAY_DURATION and self.sleepEvent.is_set():
            self.draw_screenSaver()
            display_time += 1
            self.sleepEvent.wait(1)
        
    def draw_screenSaver(self):
        
        # Set the frame index to 0
        frame_nub = 0
        self.matrix.clear()
        
        # Go through the frames
        x = 0
        while x is not 5:
            try:
                self.toaster.seek(frame_nub)
            except EOFError:
                x += 1
                frame_nub = 0
                self.toaster.seek(frame_nub)

            self.matrix.draw_image(("50%", 0), self.toaster, "center")
            self.matrix.render()

            frame_nub += 1
            sleep(0.1)
