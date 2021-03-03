#!/bin/bash

ROOT=$(dirname "$(git rev-parse --git-dir)")
CURRENTLY_BUILT_VER=$(cat "${ROOT}"/VERSION) # stored somewhere, e.g. spec file in my case
LASTVER=$(lastversion riffnshred/nhl-led-scoreboard -gt "${CURRENTLY_BUILT_VER}")
if [[ $? -eq 0 ]]; then
  # LASTVER is newer, update and trigger build
  # ....
  echo "New version V${LASTVER} available!! You are running V${CURRENTLY_BUILT_VER}"

else
  echo "You are running the latest version V${CURRENTLY_BUILT_VER}"
fi
