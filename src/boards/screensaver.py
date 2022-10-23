from PIL import Image, ImageFont, ImageDraw, ImageSequence

import driver

if driver.is_hardware():
    from rgbmatrix import graphics
else:
    from RGBMatrixEmulator import graphics

from time import sleep
import debug
from utils import center_text,get_file
import glob
import random

DISPLAY_DURATION = 5

class screenSaver:
    def __init__(self, data, matrix,sleepEvent):
        self.data = data

        self.font = data.config.layout.font
        self.matrix = matrix
        self.sleepEvent = sleepEvent

        self.brightness = self.matrix.brightness

        self.sleepEvent.clear()

        self.draw_screenSaver()


    def draw_screenSaver(self):

        self.data.screensaver_displayed = True
        show_gif = self.data.config.screensaver_animations
        all_gifs = glob.glob("assets/animations/screensaver/*.gif")
        if all_gifs and show_gif:
            filename = random.choice(all_gifs)
            debug.info("Screen saver animation is: " + filename)
            toaster = Image.open(get_file(filename))
        else:
            debug.error("No GIFs found for Screen saver animation or animations not turned on in config.json")
            show_gif = False


        i = 0
        b = self.brightness
        original_brightness = self.brightness

        while True and not self.sleepEvent.is_set():
            if show_gif:

                # Set the frame index to 0
                frame_nub = 0
                #debug.warning("In screensaver {}".format(self.sleepEvent.is_set()))
                self.matrix.clear()

                # Go through the frames
                x = 0
                while x != 10:
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

                show_gif = False
            else:
                # Fade to black
                # If user doesn't use dimmer or brightness on command line
                if b is not None:
                    while b >=0:
                        self.matrix.set_brightness(self.brightness)
                        self.brightness = b
                        self.matrix.render()
                        b -= 1
                        sleep(0.1)

                self.matrix.clear()
                self.matrix.draw.rectangle([0,0, self.matrix.width, self.matrix.height], fill=(0,0,0))
                self.matrix.render()

            i += 1
            if i % 90 == 0:
                debug.info("Screen saver is active....")

            self.sleepEvent.wait(1)

        if self.data.pb_trigger:
            # Restore original brightness after push button
            self.matrix.set_brightness(original_brightness)
            self.matrix.render()
