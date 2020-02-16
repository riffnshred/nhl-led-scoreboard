#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

# Install the latest version of Python 3
sudo apt-get update && sudo apt-get install python3-dev

# Pull submodule and ignore changes from script
git submodule update --init --recursive
git config submodule.matrix.ignore all

cd submodules/matrix || exit
echo "Running rgbmatrix installation..."
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd bindings
sudo pip3 install -e python/

cd ../../../

echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
git reset --hard
git fetch origin --prune
git pull
sudo pip3 install requests 
sudo pip3 install geocoder python_tsl2591 ephem

make
echo "If you didn't see any errors above, everything should be installed!"
echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."
