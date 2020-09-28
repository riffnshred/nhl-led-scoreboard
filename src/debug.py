#import data.scoreboard_config
import data
import time
import sys
import logging

debug_enabled = False

# Create a logger object.

#logger = logging.getLogger(__name__)
logger = logging.getLogger('scoreboard')
#Don't send our logging messages up to the root logger (stops duplicates)
logger.propagate = False


def set_debug_status(config,logcolor=False,loglevel='INFO'):
	global debug_enabled
	debug_enabled = config.debug
	colorAvail = False

	if sys.stdin.isatty() and logcolor:
		try:
			import coloredlogs
			colorAvail = True
		except Exception as e:
			colorAvail = False
			logger.error("ERROR: Unable to import module: {}  Did you install it?".format(e))


	if loglevel.lower() == "debug":
		debug_enabled = True

	if debug_enabled:
		if colorAvail:
			coloredlogs.install(level='DEBUG',fmt='%(asctime)s %(name)s %(levelname)s %(message)s',stream=sys.stdout)
		else:
			logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt='%y-%m-%d %H:%M:%S')

	else:
		if colorAvail:
			coloredlogs.install(level=loglevel,fmt='%(asctime)s %(levelname)s %(message)s',stream=sys.stdout,logger=logger)
		else:
			handler = logging.StreamHandler(sys.stdout)
			formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			logger.setLevel(loglevel)


def __debugprint(text):
	print(text)
	sys.stdout.flush()

def log(text):
	if debug_enabled:
		#__debugprint("DEBUG ({}): {}".format(__timestamp(), text))
		logger.debug(text)

def warning(text):
  #__debugprint("WARNING ({}): {}".format(__timestamp(), text))
  logger.warn(text)

def error(text):
	#__debugprint("ERROR ({}): {}".format(__timestamp(), text))
	logger.error(text)

def info(text):
	#__debugprint("INFO ({}): {}".format(__timestamp(), text))
	logger.info(text)

def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())
