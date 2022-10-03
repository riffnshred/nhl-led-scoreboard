# Version 1.0 - initial version 03/01/20
import debug
import time
import os
from gpiozero import Button
from signal import pause
from subprocess import check_call
from sbio.screensaver import screenSaver

VALID_PINS = [2,3,7,8,9,10,11,14,15,19,25]
REBOOT_DEFAULT = 2
AVAIL_BOARDS = ["team_summary","standings","scoreticker","seriesticker","clock","weather","wxalert","pbdisplay","wxforecast","screensaver","stanley_cup_champions","christmas"]

class PushButton(object):
    def __init__(self, data, matrix, sleepEvent):

        # Pins available for HAT: RX, TX, 25, MOSI, MISO, SCLK, CE0, CE1, 19.
        # Pins available on bonnet: SCL, SDA, RX, TX, #25, MOSI, MISO, SCLK, CE0, CE1, #19.
        # GPIOZero pin numbering: 7,8,9,10,11,14,15,19,25 HAT , bonnet adds 2,3

        self.data = data
        self.matrix = matrix
        self.pb_run = True
        self.sleepEvent = sleepEvent


        #Test the state_triggered1 to make sure that the board exists, if not, default to clock
        if data.config.pushbutton_state_triggered1 not in AVAIL_BOARDS:
            debug.error("Your preferred board is not one of the available boards.  Defaulting to clock.  Please change your config to select one of " + str(AVAIL_BOARDS))
            data.config.pushbutton_state_triggered1 = "clock"
        self.trigger_board = data.config.pushbutton_state_triggered1
        self.poweroff_duration = data.config.pushbutton_poweroff_duration
        self.reboot_duration = data.config.pushbutton_reboot_duration
        self.data.curr_board = "***Dummy Board***"

        # Make sure that poweroff duration is greater than reboot
        if self.poweroff_duration <= self.reboot_duration:
            #Swap the values, let the user know
            debug.error("Power off duration (" + str(self.poweroff_duration) +  "s) is less than reboot duration (" +str(self.reboot_duration) + "s), values have been swapped, please change config for next run")
            self.reboot_duration = data.config.pushbutton_poweroff_duration
            self.poweroff_duration = data.config.pushbutton_reboot_duration

        # Make sure reboot suration is not less than REBOOT_DEFAULT seconds
        if self.reboot_duration < REBOOT_DEFAULT:
            debug.error("Reboot duration (" + str(self.reboot_duration) +  "s) is less than minimum of " + str(REBOOT_DEFAULT) + "s , please change config for next run")
            self.reboot_duration = REBOOT_DEFAULT

        self.reboot_process = data.config.pushbutton_reboot_override_process
        self.poweroff_process = data.config.pushbutton_poweroff_override_process
        self.trigger1_process = data.config.pushbutton_state_triggered1_process
        self.trigger1_process_run = False
        self.display_reboot = data.config.pushbutton_display_reboot
        self.display_halt = data.config.pushbutton_display_halt


        if self.reboot_process:
            if not os.path.isfile(self.reboot_process):
                debug.error("Reboot override process does not exist or is blank in config.json, falling back to default /sbin/reboot.  Check the config.json for errors")
                self.reboot_process = "/sbin/reboot"
        else:
            self.reboot_process = "/sbin/reboot"

        if self.poweroff_process:
            if not os.path.isfile(self.poweroff_process):
                debug.error("Poweroff override process does not exist or is blank in config.json, falling back to default /sbin/poweroff.  Check the config.json for errors")
                self.poweroff_process = "/sbin/poweroff"
        else:
            self.poweroff_process = "/sbin/poweroff"

        if self.trigger1_process:
            if not os.path.isfile(self.trigger1_process):
                debug.error("State Trigger1 process does not exist or is blank in config.json, will not attempt to run.  Check the config.json for errors")
            else:
                debug.info("Process " + self.trigger1_process + " for state_triggered1 is good.")
                self.trigger1_process_run = True

        debug.info(self.reboot_process + " <-- reboot || poweroff --> " + self.poweroff_process)
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
        # Count how many times a button is pressed.  Could be used to trigger another process or board display
        self.__press_count += 1

        #Test - Uncomment to test pbdisplay
        #self.data.pb_state = "! HALT !"
        #self.data.pb_trigger = True
        #self.data.config.pushbutton_state_triggered1 = "pbdisplay"
        #self.sleepEvent.set()

    def on_release(self):
        release_time = time.time()
        held_for = release_time - self.__press_time


        if held_for >= self.reboot_duration and held_for < self.poweroff_duration:
            self.__press_count = 0
            debug.info("reboot process " + self.reboot_process + " triggered after " + str(self.reboot_duration) + " seconds (actual held time = " + str(held_for) + ")")
            self.data.pb_state = "REBOOT"
            # Call display
            if self.display_reboot:
                self.data.pb_trigger = True
                self.data.config.pushbutton_state_triggered1 = "pbdisplay"
                self.sleepEvent.set()
                time.sleep(2)
            try:
                check_call([self.reboot_process])
            except CalledProcessError as e:
                debug.error("Unable to run " + self.reboot_process + "Error: " + format(e))
        else:
            if self.data.curr_board != self.trigger_board:
                if self.trigger1_process_run:
                    debug.info("Running " + self.trigger1_process)
                    try:
                        check_call([self.trigger1_process])
                    except CalledProcessError as e:
                        debug.error("Unable to run " + self.trigger1_process + "Error: " + format(e))

                debug.info("Trigger fired...." + self.trigger_board + " will be shown on next loop. Currently displayed board " + self.data.curr_board)
                self.data.pb_trigger = True
                self.sleepEvent.set()

            else:
                debug.info("Trigger board " + self.trigger_board + " is the same as currently displayed board " + self.data.curr_board + " killing and going back to previous board")
                self.sleepEvent.set()


    def on_hold(self):
        debug.info("power off process " + self.poweroff_process + " triggered after " + str(self.poweroff_duration) + " seconds")
        self.data.pb_state = "! HALT !"
        # Call display
        if self.display_halt:
            self.data.pb_trigger = True
            self.data.config.pushbutton_state_triggered1 = "pbdisplay"
            self.sleepEvent.set()
            time.sleep(2)

        try:
            check_call([self.poweroff_process])
        except CalledProcessError as e:
            debug.error("Unable to run " + self.poweroff_process + "Error: " + format(e))

    def run(self):
        if self.pb_run:
            pause() # wait forever
        else:
            pass