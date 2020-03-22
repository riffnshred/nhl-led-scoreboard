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
from renderer.matrix import Matrix
import debug

SCRIPT_NAME = "NHL-LED-SCOREBOARD"

SCRIPT_VERSION = "1.1.2"


def run():
    # Get supplied command line arguments
    commandArgs = args()

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

    MainRenderer(matrix, data, sleepEvent).render()

if __name__ == "__main__":
    try:
        run()

    except KeyboardInterrupt:
        print("Exiting NHL-LED-SCOREBOARD\n")
        sys.exit(0)
