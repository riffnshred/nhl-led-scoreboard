import debug
import time
from gpiozero import Button
from signal import pause
from subprocess import check_call

VALID_PINS = [2,3,7,8,9,10,11,14,15,19,25]

class PushButton(object):
    def __init__(self, data, matrix):

        # Pins available for HAT: RX, TX, 25, MOSI, MISO, SCLK, CE0, CE1, 19.
        # Pins available on bonnet: SCL, SDA, RX, TX, #25, MOSI, MISO, SCLK, CE0, CE1, #19.
        # GPIOZero pin numbering: 14,15,10,9,11,19,25,8,7 (bonnet) HAT adds 2,3
        
        self.data = data
        self.matrix = matrix
        self.pb_run = True

        self.poweroff_duration = data.config.pushbutton_poweroff_duration
        self.reboot_duration = data.config.pushbutton_reboot_duration
        self.__press_time = None
        self.__press_count = 0

        #Get the GPIO button config from the config file
        #Make sure pin selected is in list
        self.bonnet = data.config.pushbutton_bonnet
        try:
            if data.config.pushbutton_pin in VALID_PINS:
               if not self.bonnet and (data.config.pushbutton_pin in [2,3]):
                  raise ValueError("You can not use pin # " + str(data.config.pushbutton_pin) + " with the Adafruit RGB HAT. Valid gpiozero numbered pins: 7,8,9,10,11,14,15,19,25")
               else:
                  self.use_button = data.config.pushbutton_pin
                  self.button=Button(self.use_button, hold_time=self.poweroff_duration)
                  self.button.when_held = self.on_hold
                  self.button.when_released = self.on_release
                  self.button.when_pressed = self.on_press
            else:
                raise ValueError("You can not use pin # " + str(data.config.pushbutton_pin) + " with the Adafruit RGB Bonnet. Valid gpiozero numbered pins: 2,3,7,8,9,10,11,14,15,19,25")
        except ValueError as exp:
            debug.error("PushButton will not work and is now disabled.  Error: " + format(exp))
            self.pb_run = False
        

    def on_press(self):
        self.__press_time = time.time()
        self.__press_count += 1
        debug.info("Now showing! " + str(self.__press_time))
        
    def on_release(self):
        release_time = time.time()
        held_for = release_time - self.__press_time
        debug.info("Released....." + str(held_for))
        if (held_for >= self.reboot_duration):
            debug.info("reboot triggered after " + str(self.reboot_duration) + " seconds (actual held time = " + str(held_for) + ")")
            #check_call(['/sbin/reboot'])
        else:
            debug.info("Trigger something..." + str(self.__press_count))
            self.data.pb_trigger = True
            self.__press_count = 0
            
    def on_hold(self):
        debug.info("power off triggered after " + str(self.poweroff_duration) + " seconds")
        #check_call(['/sbin/poweroff'])

    def run(self):
        if self.pb_run:
            pause() # wait forever
        else:
            pass