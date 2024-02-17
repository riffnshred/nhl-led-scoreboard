#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit

tput bold; echo "$(tput setaf 2)Installing required OS dependencies. This may take some time (10-20 minutes-ish)...$(tput setaf 9)" ; tput sgr0

#Install all apt requirements using aptfile
sudo scripts/aptfile apt-requirements

tput bold; echo "$(tput setaf 2)Creating python virtual environment...$(tput setaf 9)" ; tput sgr0

#Install all apt requirements using aptfile
#sudo scripts/aptfile apt-requirements

# Update system pip3 to latest version
python3 -m pip install --upgrade pip --break-system-packages

# Install virtual enviroment, required for upcoming bookworm release
# Use already installed site-packages that were installed as part o fthe apt OS dependencies
python3 -m venv $HOME/nhlsb-venv --system-site-packages

# Activate the direnv to allow for automatic activate and deactivate of venv
tput bold; echo "$(tput setaf 2)Activating direnv for python venv...$(tput setaf 9)" ; tput sgr0

echo "export VIRTUAL_ENV=~/nhlsb-venv" >> .envrc
echo "source ~/nhlsb-venv/bin/activate" >> .envrc
direnv allow .

# Update bashrc
tee -a  ~/.bashrc << 'TEXT0'
show_virtual_env() {
  if [[ -n "$VIRTUAL_ENV" && -n "$DIRENV_DIR" ]]; then
    echo "($(basename $VIRTUAL_ENV)) "
  fi
}
export -f show_virtual_env
PS1='$(show_virtual_env)'$PS1

eval "$(direnv hook bash)"

TEXT0

echo "$(tput setaf 6)Activating python virtual environment...$(tput setaf 9)"

source $HOME/nhlsb-venv/bin/activate

echo "$(tput setaf 6)Updating pip in virtual environment...$(tput setaf 9)"
# Update pip in the virtual enviroment
python3 -m pip install --upgrade pip
#Install all pip3 requirements using the requirements.txt file
#This will install into the virtual environment

tput bold; echo "$(tput setaf 2)Installing scoreboard python requirements in virtual environment...$(tput setaf 9)" ; tput sgr0
pip3 install -r requirements.txt

# Pull submodule and ignore changes from script
git submodule update --init --recursive
git config submodule.matrix.ignore all

tput bold; echo "$(tput setaf 4)Running rgbmatrix installation...$(tput setaf 9)" ; tput sgr0

# No longer needed for newer version of the rgb matric repo as of Dec 2021
# Recompile the cpp files to build library with newest cython.  See https://github.com/hzeller/rpi-rgb-led-matrix/issues/1298

cd submodules/matrix/ || exit

# python3 -m pip install --no-cache-dir cython
# python3 -m cython -2 --cplus *.pyx

# cd ../../ || exit

make build-python PYTHON="$(command -v python3)"
make install-python PYTHON="$(command -v python3)"

cd ../../ || exit

# Blacklist the snd_bcm2835 sounds module
sudo tee /etc/modprobe.d/blacklist-rgbmatrix.conf <<TEXT1
## Make sure the sound module does not load as it causes issues with the timing for the rgb matrix library
blacklist snd_bcm2835

# The next time the loading of the module is attempted, the /bin/false
# will be executed instead. This will prevent the module from being
# loaded on-demand.

install snd_bcm_2835 /bin/false

TEXT1

# Unload the sound module
sudo modprobe -r snd_bcm2835

# Rebuild module dependacy
sudo depmod -a

sudo sed -i 's/$/ isolcpus=3/' /boot/cmdline.txt

git reset --hard
git fetch origin --prune
git pull

tput bold; echo "$(tput setaf 6)If you didn't see any errors above, everything should be installed!"; tput sgr0
echo "$(tput bold)$(tput smso)$(tput setaf 2)Installation complete!$(tput sgr0) Play around with the examples in nhl-led-scoreboard/submodules/matrix/bindings/python/samples to make sure your matrix is working."
tput bold; echo "$(tput setaf 4)...................................................$(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 4)TAKE NOTE OF NEXT LINES...$(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 4)WITh A VENV, Your python is now located differently...$(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 4)TO RUN WITH SUDO, YOU MUST USE THE VENV LOCATION...$(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 4).................PYTHON LOOKS LIKE.....................$(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 1)sudo $HOME/nhlsb-venv/bin/python3 $(tput setaf 9)" ; tput sgr0
tput bold; echo "$(tput setaf 4)...................................................$(tput setaf 9)" ; tput sgr0
