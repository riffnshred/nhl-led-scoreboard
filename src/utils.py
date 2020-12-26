from rgbmatrix import RGBMatrixOptions, graphics
import collections
import argparse
import os
import debug
from datetime import datetime, timezone, time
import regex
import math
import geocoder

def get_lat_lng(location):

    if len(location) > 0:
        try:
            g = geocoder.osm(location)
            debug.info("location is: " + location + " " + str(g.latlng))
        except Exception as e:
            debug.error("Unable to find {} with Open Street Map, falling back to IP lookup for location.  Error: {}".format(location,e))
            g = geocoder.ip('me')
            debug.info("location is: " + g.city + ","+ g.country + " " + str(g.latlng))
    else:
        g = geocoder.ip('me')
        debug.info("location is: " + g.city + ","+ g.country + " " + str(g.latlng))

    return g.latlng

# validate if a string is in 12h format or 24h format
def timeValidator(timestr):
    #Check 24hr HH:MM
    ok24hr = regex.match('^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$', timestr)
    #Check 12h 5:30 PM or 5:30 pm 
    ok12hr = regex.match('^(1[0-2]|0?[1-9]):([0-5][0-9]) ([AaPp][Mm])$',timestr)

    if ok24hr:
        return "24h"
    elif ok12hr:
        return "12h"
    else:
        return "invalid"

    

def get_file(path):
    dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(dir, path)


def split_string(string, num_chars):
    return [(string[i:i + num_chars]).strip() for i in range(0, len(string), num_chars)]


def args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--testScChampions", action="store", help="A flag to test the stanley cup champions board. Put your team's ID", default=None, type=int)
    parser.add_argument("--test-goal-animation", action="store", help="A flag to test the goal animation", default=None, type=bool)
    parser.add_argument("--testing-mode", action="store", help="Allow to put use a loop in the renderer to do testing. For Development only")

    # Options for the rpi-rgb-led-matrix library
    parser.add_argument("--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. (Default: 32)",
                        default=32, type=int)
    parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 64)",
                        default=64, type=int)
    parser.add_argument("--led-chain", action="store", help="Daisy-chained boards. (Default: 1)", default=1, type=int)
    parser.add_argument("--led-parallel", action="store",
                        help="For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)", default=1, type=int)
    parser.add_argument("--led-pwm-bits", action="store", help="Bits used for PWM. Range 1..11. (Default: 11)",
                        default=11, type=int)
    parser.add_argument("--led-brightness", action="store", help="Sets brightness level. Range: 1..100. (Default: 100)",
                        default=100, type=int)
    parser.add_argument("--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
                        choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
    parser.add_argument("--led-scan-mode", action="store",
                        help="Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)", default=1,
                        choices=range(2), type=int)
    parser.add_argument("--led-pwm-lsb-nanoseconds", action="store",
                        help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)",
                        default=130, type=int)
    parser.add_argument("--led-pwm-dither-bits", action="store",
                        help="Time dithering of lower bits (Default: 0)",
                        default=0, type=int)
    parser.add_argument("--led-show-refresh", action="store_true",
                        help="Shows the current refresh rate of the LED panel.")
    parser.add_argument("--led-slowdown-gpio", action="store",
                        help="Slow down writing to GPIO. Range: 0..4. (Default: 1)", choices=range(5), type=int)
    parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation.")
    parser.add_argument("--led-rgb-sequence", action="store",
                        help="Switch if your matrix has led colors swapped. (Default: RGB)", default="RGB", type=str)
    parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="",
                        type=str)
    parser.add_argument("--led-row-addr-type", action="store",
                        help="0 = default; 1 = AB-addressed panels; 2 = direct row select; 3 = ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0, 1, 2, 3, 4])
    parser.add_argument("--led-multiplexing", action="store",
                        help="Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; 5 = ZnMirrorZStripe; 6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)",
                        default=0, type=int)
    parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)
    parser.add_argument("--terminal-mode", action="store", help="Run on terminal instead of matrix. (Default: False)", default=False, type=bool)                     
    parser.add_argument("--updatecheck", action="store_true", help="Check for updates (Default: False)", default=False)
    parser.add_argument("--updaterepo", action="store", help="Github repo (Default: riffnshred/nhl-scoreboard)", default="riffnshred/nhl-led-scoreboard", type=str)
    parser.add_argument("--ghtoken", action="store", help="Github API token for doing update checks(Default: blank)", default="", type=str)
    parser.add_argument("--logcolor", action="store_true", help="Display log in color (command line only)")
    parser.add_argument("--loglevel", action="store", help="log level to display (INFO,WARN,ERROR,CRITICAL,DEBUG)", type=str)


    return parser.parse_args()


def led_matrix_options(args):
    options = RGBMatrixOptions()

    if args.led_gpio_mapping != None:
        options.hardware_mapping = args.led_gpio_mapping

    options.rows = args.led_rows
    options.cols = args.led_cols
    options.chain_length = args.led_chain
    options.parallel = args.led_parallel
    options.row_address_type = args.led_row_addr_type
    options.multiplexing = args.led_multiplexing
    options.pwm_bits = args.led_pwm_bits
    options.brightness = args.led_brightness
    options.pwm_lsb_nanoseconds = args.led_pwm_lsb_nanoseconds
    options.led_rgb_sequence = args.led_rgb_sequence
    options.panel_type = args.led_panel_type
    try:
        options.pixel_mapper_config = args.led_pixel_mapper
    except AttributeError:
        debug.warning("Your compiled RGB Matrix Library is out of date.")
        debug.warning("The --led-pixel-mapper argument will not work until it is updated.")
    

    if args.led_show_refresh:
        options.show_refresh_rate = 1

    if args.led_slowdown_gpio != None:
        options.gpio_slowdown = args.led_slowdown_gpio

    if args.led_no_hardware_pulse:
        options.disable_hardware_pulsing = True

    return options


def deep_update(source, overrides):
    """
        Update a nested dictionary or similar mapping.
        Modify ``source`` in place.
    """
    for key, value in list(overrides.items()):
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def convert_time(utc_dt):
    local_dt = datetime.strptime(utc_dt, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
    return local_dt


def is_empty_list(list):
    return not len(list)


def read_json(self, filename):
    # Find and return a json file

    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
        j = json.load(open(path))
    return j

def center_text(text_width, center_pos):
    return abs(center_pos - (text_width / 2))

def center_obj(screen_w, lenght):
    """
        Center any object on screen. If width is odd number of pixel, bump right of one pixel
    :return:
    """
    return int((screen_w - lenght)/2)

def convert_date_format(date):
    d = datetime.strptime(date, '%Y-%m-%d')
    return d.strftime('%b %d')

def round_normal(n, decimals=0):
    multiplier = 10 ** decimals
    value = math.floor(n * multiplier + 0.5) / multiplier
    return int(value) if decimals == 0 else value
