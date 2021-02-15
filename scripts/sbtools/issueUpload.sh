#!/bin/bash
# Upload the scoreboard stderr, stdout and config.json to pastebin using pastebinit
if [ -n "${1}" ]; then
   scoreboard_proc=$1
else
   scoreboard_proc="scoreboard"
fi

#Create temp file with the data
ROOT=$(/usr/bin/dirname "$(/usr/bin/git rev-parse --git-dir)")
version=$(/bin/cat "${ROOT}"/VERSION)
currdate=$(date)
echo "nhl-led-scoreboard issue data ${currdate}" > /tmp/issue.txt
echo "=============================" >>/tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "Running V${version} on a " >> /tmp/issue.txt
/usr/bin/neofetch --off --stdout | grep Host >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "config.json" >> /tmp/issue.txt
echo "" >>/tmp/issue.txt
/usr/bin/jq '.boards.weather.owm_apikey=""' "${ROOT}"/config/config.json >> /tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "supervisorctl status" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
/usr/local/bin/supervisorctl status >>/tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "${scoreboard_proc} stderr log, last 50kb" >> /tmp/issue.txt
echo "=================================" >> /tmp/issue.txt
/usr/local/bin/supervisorctl tail -50000 $scoreboard_proc stderr >> /tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "${scoreboard_proc} stdout log, last 50kb" >> /tmp/issue.txt
echo "=================================" >> /tmp/issue.txt
/usr/local/bin/supervisorctl tail -50000 $scoreboard_proc >> /tmp/issue.txt
url=$(/usr/bin/pastebinit -b paste.ubuntu.com -t "nhl-led-scoreboard issue logs and config" < /tmp/issue.txt)
echo "Take this url and paste it into your issue.  You can create an issue @ https://github.com/riffnshred/nhl-led-scoreboard/issues"
echo "${url}"
rm /tmp/issue.txt