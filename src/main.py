import sys
from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
import threading
from sbio.dimmer import Dimmer
from sbio.pushbutton import PushButton
from renderer.matrix import Matrix, TermMatrix
from api.weather.ecWeather import ecWxWorker
from api.weather.owmWeather import owmWxWorker
from api.weather.ecAlerts import ecWxAlerts
from api.weather.nwsAlerts import nwsWxAlerts
from renderer.matrix import Matrix
from update_checker import UpdateChecker
from apscheduler.schedulers.background import BackgroundScheduler
import debug
import os

SCRIPT_NAME = "NHL-LED-SCOREBOARD"

SCRIPT_VERSION = "1.4.1"


def run():
    # Get supplied command line arguments
    commandArgs = args()

    if commandArgs.terminal_mode:
        height, width = os.popen('stty size', 'r').read().split()
        termMatrix = TermMatrix()
        termMatrix.width = int(width)
        termMatrix.height = int(height)
        matrix = Matrix(termMatrix)
    else:
        # Check for led configuration arguments
        matrixOptions = led_matrix_options(commandArgs)
        matrixOptions.drop_privileges = False

        # Initialize the matrix
        matrix = Matrix(RGBMatrix(options = matrixOptions))

    # Print some basic info on startup
    debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

    # Read scoreboard options from config.json if it exists
    config = ScoreboardConfig("config", commandArgs, (matrix.width, matrix.height))

    debug.set_debug_status(config)

    data = Data(config)

    # Event used to sleep when rendering
    # Allows Web API (coming in V2) and pushbutton to cancel the sleep
    # Will also allow for weather alert to interrupt display board if you want
    sleepEvent = threading.Event()

    if data.config.dimmer_enabled:
        dimmer = Dimmer(data, matrix)
        dimmerThread = threading.Thread(target=dimmer.run, args=())
        dimmerThread.daemon = True
        dimmerThread.start()

    if data.config.pushbutton_enabled:
        pushbutton = PushButton(data,matrix,sleepEvent)
        pushbuttonThread = threading.Thread(target=pushbutton.run, args=())
        pushbuttonThread.daemon = True
        pushbuttonThread.start()
    
    if data.config.weather_enabled:
        if data.config.weather_data_feed.lower() == "owm":
            owmweather = owmWxWorker(data,sleepEvent)
            owmweatherThread = threading.Thread(target=owmweather.run,args=())
            owmweatherThread.daemon = True
            owmweatherThread.start()
        elif data.config.weather_data_feed.lower() == "ec":
            ecweather = ecWxWorker(data,sleepEvent)
            ecweatherThread = threading.Thread(target=ecweather.run,args=())
            ecweatherThread.daemon = True
            ecweatherThread.start()
        else:
            debug.error("No valid weather providers selected, skipping weather feed")
            data.config.weather_enabled = False

    if data.config.wxalert_show_alerts:
        if data.config.wxalert_alert_feed.lower() == "ec":
            ecalert = ecWxAlerts(data,sleepEvent)
            ecalertThread = threading.Thread(target=ecalert.run,args=())
            ecalertThread.daemon = True
            ecalertThread.start()
        elif data.config.wxalert_alert_feed.lower() == "nws":
            nwsalert = nwsWxAlerts(data,sleepEvent)
            nwsalertThread = threading.Thread(target=nwsalert.run,args=())
            nwsalertThread.daemon = True
            nwsalertThread.start()
        else:
            debug.error("No valid weather alerts providers selected, skipping alerts feed")
            data.config.weather_show_alerts = False
    
    #
    # Run check for updates against github on a background thread on a scheduler
    #     

    if commandArgs.updatecheck:
        data.UpdateRepo = commandArgs.updaterepo
        scheduler = BackgroundScheduler()
        checkupdate = UpdateChecker(data,scheduler)
        scheduler.start()

    MainRenderer(matrix, data, sleepEvent).render()


if __name__ == "__main__":
    try:
        run()

    except KeyboardInterrupt:
        print("Exiting NHL-LED-SCOREBOARD\n")
        sys.exit(0)
