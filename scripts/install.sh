#! /bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit

# Don't run as root user
if [ $(id -u) -eq 0 ]; then
  tput bold; echo "$(tput setaf 9)You do not need to run this script using sudo, it will handle sudo as required$(tput setaf 9)" ; tput sgr0
  exit 1
fi

deb_ver () {
  ver=$(cut -d . -f 1 < /etc/debian_version)
  echo $ver
}

deb_name () {
    . /etc/os-release; echo "$PRETTY_NAME"
}	

py_ver () {
  pyver="$(command -p python3 -V | sed 's/Python //g')"
  echo $pyver
}

show_virtual_env() {
  if [ -n "$VIRTUAL_ENV" ]; then
    echo "VENV name: $(basename $VIRTUAL_ENV)"
  else
    echo "No VENV installed"
  fi
}

py_loc () {
  pyloc="$(command -v python3)"
  echo $pyloc
}

get_model() {
	pimodel=$(tr -d '\0' </proc/device-tree/model)
	echo $pimodel
}

calc_wt_size() {
  # NOTE: it's tempting to redirect stderr to /dev/null, so supress error
  # output from tput. However in this case, tput detects neither stdout or
  # stderr is a tty and so only gives default 80, 24 values
  WT_HEIGHT=18
  WT_WIDTH=$(tput cols)

  if [ -z "$WT_WIDTH" ] || [ "$WT_WIDTH" -lt 60 ]; then
    WT_WIDTH=80
  fi
  if [ "$WT_WIDTH" -gt 178 ]; then
    WT_WIDTH=120
  fi
  WT_MENU_HEIGHT=$((WT_HEIGHT - 7))
}

do_install() {
	scripts/sbtools/sb-init
  exit 0
}

do_upgrade() {
  scripts/sbtools/sb-upgrade
  exit 0
}

do_help() {
 whiptail --msgbox "\
This tool provides a straightforward way of doing initial
install of the NHL LED Scoreboard or an Upgrade of an existing installation\
" 20 70 1
  return 0
}

calc_wt_size

backtitle="$(get_model) [$(deb_name)] [Python: $(py_loc) V$(py_ver) $(show_virtual_env)]"

while true; do

        FUN=$(whiptail --title "NHL LED Scoreboard Install/Upgrade Tool" --backtitle "$backtitle" --menu "Options" $WT_HEIGHT $WT_WIDTH $WT_MENU_HEIGHT --cancel-button Finish --ok-button Select \
        "1 New Install" "Use this if this is your first time installing" \
        "2 Upgrade" "Use this if you are upgrading" \
        "3 Help" "Show help for this tool" \
        3>&1 1>&2 2>&3)

	RET=$?

	if [ $RET -eq 1 ]; then
           exit 0
        elif [ $RET -eq 0 ]; then
          case "$FUN" in
            1\ *) do_install ;;
            2\ *) do_upgrade ;;
            3\ *) do_help ;;
            *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
          esac || whiptail --msgbox "There was an error running option $FUN" 20 60 1
        else
      exit 1
    fi
done
