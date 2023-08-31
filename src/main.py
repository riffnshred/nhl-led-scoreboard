import sys
import time
import driver
from datetime import datetime, timedelta

from apscheduler.events import EVENT_ALL, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from utils import args, led_matrix_options, scheduler_event_listener
from data.data import Data
import queue
import threading
from renderer.matrix import Matrix
from api.weather.ecWeather import ecWxWorker
from api.weather.owmWeather import owmWxWorker
from api.weather.ecAlerts import ecWxAlerts
from api.weather.nwsAlerts import nwsWxAlerts
from api.weather.wxForecast import wxForecast
import asyncio
from env_canada import ECWeather
from update_checker import UpdateChecker
import tzlocal
from apscheduler.schedulers.background import BackgroundScheduler
from renderer.loading_screen import Loading
import debug
import os
# If you want real fancy stack trace dumps, uncomment these two lines
#from rich.traceback import install
#install(show_locals=True)  

SCRIPT_NAME = "NHL-LED-SCOREBOARD"

SCRIPT_VERSION = "1.7.0"

# Conditionally load the appropriate driver classes and set the global driver mode based on command line flags

if args().emulated:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

    driver.mode = driver.DriverMode.SOFTWARE_EMULATION
else:
    try:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        from utils import stop_splash_service

        driver.mode = driver.DriverMode.HARDWARE
    except ImportError:
        from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

        driver.mode = driver.DriverMode.SOFTWARE_EMULATION

def run():
    # Get supplied command line arguments
    commandArgs = args()
    if driver.is_hardware():
        # Kill the splash screen if active
        stop_splash_service()

    # Check for led configuration arguments
    matrixOptions = led_matrix_options(commandArgs)
    matrixOptions.drop_privileges = False

    # Initialize the matrix
    matrix = Matrix(RGBMatrix(options = matrixOptions))

     #Riff to add loading screen here
    loading = Loading(matrix)
    loading.render()

    # Read scoreboard options from config.json if it exists
    config = ScoreboardConfig("config", commandArgs, (matrix.width, matrix.height))

    data = Data(config)

    #If we pass the logging arguments on command line, override what's in the config.json, else use what's in config.json (color will always be false in config.json)
    if commandArgs.logcolor and commandArgs.loglevel != None:
        debug.set_debug_status(config,logcolor=commandArgs.logcolor,loglevel=commandArgs.loglevel)
    elif not commandArgs.logcolor and commandArgs.loglevel != None:
        debug.set_debug_status(config,loglevel=commandArgs.loglevel)
    elif commandArgs.logcolor and commandArgs.loglevel == None:
        debug.set_debug_status(config,logcolor=commandArgs.logcolor,loglevel=config.loglevel)
    else:
        debug.set_debug_status(config,loglevel=config.loglevel)

    # Print some basic info on startup
    debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))
    
    if data.latlng is not None:
        debug.info(data.latlng_msg)
    else:
        debug.error("Unable to find your location.")

    # Event used to sleep when rendering
    # Allows Web API (coming in V2) and pushbutton to cancel the sleep
    # Will also allow for weather alert to interrupt display board if you want
    sleepEvent = threading.Event()

    # Start task scheduler, used for UpdateChecker and screensaver, forecast, dimmer and weather
    scheduler = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), job_defaults={'misfire_grace_time': None})
    scheduler.add_listener(scheduler_event_listener, EVENT_JOB_MISSED | EVENT_JOB_ERROR)
    scheduler.start()

    # Any tasks that are scheduled go below this line

    # Make sure we have a valid location for the data.latlng as the geocode can return a None
    # If there is no valid location, skip the weather boards
   
    #Create EC data feed handler
    if data.config.weather_enabled or data.config.wxalert_show_alerts:
        if data.config.weather_data_feed.lower() == "ec" or data.config.wxalert_alert_feed.lower() == "ec":           
             data.ecData = ECWeather(coordinates=(tuple(data.latlng)))
             try:
                asyncio.run(data.ecData.update())
             except Exception as e:
                debug.error("Unable to connect to EC .. will try on next refresh : {}".format(e))
            
    if data.config.weather_enabled:
        if data.config.weather_data_feed.lower() == "ec":
            ecWxWorker(data,scheduler)
        elif data.config.weather_data_feed.lower() == "owm":
            owmweather = owmWxWorker(data,scheduler)
        else:
            debug.error("No valid weather providers selected, skipping weather feed")
            data.config.weather_enabled = False


    if data.config.wxalert_show_alerts:
        if data.config.wxalert_alert_feed.lower() == "ec":
            ecalert = ecWxAlerts(data,scheduler,sleepEvent)
        elif data.config.wxalert_alert_feed.lower() == "nws":
            nwsalert = nwsWxAlerts(data,scheduler,sleepEvent)
        else:
            debug.error("No valid weather alerts providers selected, skipping alerts feed")
            data.config.weather_show_alerts = False

    if data.config.weather_forecast_enabled and data.config.weather_enabled:
        wxForecast(data,scheduler)
    #
    # Run check for updates against github on a background thread on a scheduler
    #
    if commandArgs.updatecheck:
        data.UpdateRepo = commandArgs.updaterepo
        checkupdate = UpdateChecker(data,scheduler,commandArgs.ghtoken)

    # If the driver is running on actual hardware, these files contain libs that should be installed.
    # For other platforms, they probably don't exist and will crash.
    screensaver = None 
    
    if driver.is_hardware():
        from sbio.dimmer import Dimmer
        from sbio.pushbutton import PushButton
        from sbio.motionsensor import Motion
        from sbio.screensaver import screenSaver

        if data.config.dimmer_enabled:
            dimmer = Dimmer(data, matrix,scheduler)

        
        if data.config.screensaver_enabled:
            screensaver = screenSaver(data, matrix, sleepEvent, scheduler)
            if data.config.screensaver_motionsensor:
                motionsensor = Motion(data,matrix,sleepEvent,scheduler,screensaver)
                motionsensorThread = threading.Thread(target=motionsensor.run, args=())
                motionsensorThread.daemon = True
                motionsensorThread.start()

        if data.config.pushbutton_enabled:
            pushbutton = PushButton(data,matrix,sleepEvent)
            pushbuttonThread = threading.Thread(target=pushbutton.run, args=())
            pushbuttonThread.daemon = True
            pushbuttonThread.start()
    
    mqtt_enabled = data.config.mqtt_enabled
    # Create a queue for scoreboard events and info to be sent to an MQTT broker
    sbQueue = queue.Queue()
    pahoAvail = False
    if mqtt_enabled:     
        # Only import if we are actually using mqtt, that way paho_mqtt doesn't need to be installed
        try:
            from sbio.sbMQTT import sbMQTT
            pahoAvail = True
        except Exception as e:
            debug.error("MQTT (paho-mqtt): is disabled.  Unable to import module: {}  Did you install paho-mqtt?".format(e))
            pahoAvail = False   
        
        if pahoAvail:
            sbmqtt = sbMQTT(data,matrix,sleepEvent,sbQueue,screensaver)
            sbmqttThread = threading.Thread(target=sbmqtt.run, args=())
            sbmqttThread.daemon = True
            sbmqttThread.start()
    
    MainRenderer(matrix, data, sleepEvent,sbQueue).render()


if __name__ == "__main__":
    try:
        run()

    except KeyboardInterrupt:
        print("Exiting NHL-LED-SCOREBOARD\n")
        sys.exit(0)
