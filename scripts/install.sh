#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

# Install the latest version of pip3
sudo apt-get update
sudo apt install git python3-pip

# Install the latest version of Python 3
sudo apt-get install python3-dev

sudo apt-get install python3-setuptools
sudo apt-get install build-essential

# Pull submodule and ignore changes from script
git submodule update --init --recursive
git config submodule.matrix.ignore all

sudo apt-get -y install python3-dev python3-pillow

cd submodules/matrix || exit
echo "Running rgbmatrix installation..."

make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd bindings
sudo pip3 install --ignore-installed -e python/

cd ../../../

echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
git reset --hard
git fetch origin --prune
git pull

sudo pip3 install requests 
sudo pip3 install regex

# For dimmer
sudo pip3 install geocoder python_tsl2591 ephem

# For weather
sudo pip3 uninstall numpy
sudo apt-get install python3-numpy
sudo apt-get install libatlas3-base
sudo pip3 install env-canada==0.0.35
sudo pip3 install --upgrade pyowm
sudo pip3 install noaa_sdk fastjsonschema
sudo apt-get install libatlas-base-dev

# For update checker
sudo pip3 install apscheduler
sudo pip3 install lastversion

# For push button
sudo apt-get -y install python3-gpiozero

# For terminal mode
sudo apt-get install libatlas-base-dev
sudo pip3 install numpy

# For svgs
sudo apt-get -y install python3-cairosvg
sudo apt-get -y install libraqm-dev

make
echo "If you didn't see any errors above, everything should be installed!"
echo "Installation complete! Play around with the examples in nhl-led-scoreboard/submodules/matrix/bindings/python/samples to make sure your matrix is working."
