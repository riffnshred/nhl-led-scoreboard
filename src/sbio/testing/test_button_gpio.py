from gpiozero import Button
from time import sleep

GPIOPIN = int(input("Which GPIO number is your button connected too?:"))
button = Button(GPIOPIN)

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")
    
    sleep(0.1)