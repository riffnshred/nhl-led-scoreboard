#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

sudo python3 src/main.py --led-gpio-mapping=adafruit-hat-pwm --led-slowdown-gpio=3