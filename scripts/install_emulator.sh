#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit

echo "$(tput setaf 6)Installing required dependencies. This may take some time...$(tput setaf 9)"
#Install all pip3 requirements using the emulator_requirements.txt filer
sudo pip3 install -r emulator_requirements.txt

git reset --hard
git fetch origin --prune
git pull

echo "If you didn't see any errors above, everything should be installed!"
echo "$(tput bold)$(tput smso)$(tput setaf 2)Installation complete!$(tput sgr0)"
