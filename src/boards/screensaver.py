from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
import debug
from utils import center_text,get_file
import glob
import random

DISPLAY_DURATION = 5

class screenSaver:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data
        self.status = self.data.screensaver_displayed
        self.font = data.config.layout.font   
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        self.draw_screenSaver()
        
            
        
    def draw_screenSaver(self):
        
        self.status = True
        show_gif = self.data.config.screensaver_animations
        all_gifs = glob.glob("assets/animations/screensaver/*.gif")
        if all_gifs and show_gif:
            filename = random.choice(all_gifs)
            debug.info("Screen saver animation is: " + filename)
        else:
            debug.error("No GIFs found for Screen saver animation")
            show_gif = False

        toaster = Image.open(get_file(filename))
        i = 0
        while True and not self.sleepEvent.is_set():
            if show_gif:
                # Set the frame index to 0
                frame_nub = 0
                #debug.warning("In screensaver {}".format(self.sleepEvent.is_set()))
                self.matrix.clear()
                
                # Go through the frames
                x = 0
                while x is not 10:
                    try:
                        toaster.seek(frame_nub)
                    except EOFError:
                        x += 1
                        frame_nub = 0
                        toaster.seek(frame_nub)

                    self.matrix.draw_image(("50%", 0), toaster, "center")
                    self.matrix.render()

                    frame_nub += 1
                    sleep(0.1)
                
                self.matrix.clear()
                self.matrix.render()
                show_gif = False
            else:
                self.matrix.clear()
                self.matrix.draw.rectangle([0,0, self.matrix.width, self.matrix.height], fill=(0,0,0))
                self.matrix.render()
            
            i += 1
            if i % 90 == 0:
                debug.info("Screen saver is active....")
                
            self.sleepEvent.wait(1)
