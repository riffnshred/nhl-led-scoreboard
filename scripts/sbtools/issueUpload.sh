#!/bin/bash
# Upload the scoreboard stderr, stdout and config.json to pastebin using pastebinit

#Create temp file with the data
ROOT=`dirname $(git rev-parse --git-dir)`
version=`cat ${ROOT}/VERSION`
currdate=`date`
echo "nhl-led-scoreboard issue data ${currdate}" > /tmp/issue.txt
echo "=============================" >>/tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "Running V${version} on a " >> /tmp/issue.txt
echo `neofetch --off --stdout | grep Host` >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "config.json" >> /tmp/issue.txt
echo "" >>/tmp/issue.txt
jq '.boards.weather.owm_apikey=""' ${ROOT}/config/config.json >> /tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "supervisorctl status" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
supervisorctl status >>/tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "scoreboard stderr log, first 128kb" >> /tmp/issue.txt
echo "=================================" >> /tmp/issue.txt
supervisorctl tail -128000 scoreboard stderr >> /tmp/issue.txt
echo "" >> /tmp/issue.txt
echo "------------------------------------------------------" >> /tmp/issue.txt
echo "scoreboard stdout log, first 128kb" >> /tmp/issue.txt
echo "=================================" >> /tmp/issue.txt
supervisorctl tail -128000 scoreboard >> /tmp/issue.txt
url=`pastebinit -b paste.ubuntu.com -t "nhl-led-scoreboard issue logs and config" < /tmp/issue.txt`
echo "Take this url and paste it into your issue.  You can create an issue @ https://github.com/riffnshred/nhl-led-scoreboard/issues"
echo "${url}"
#rm /tmp/issue.txt
