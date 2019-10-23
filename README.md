# NHL-LED-scoreboard
![scoreboard demo](imgs/scoreboard.jpg)

Display NHL score of your favorite team's game on a Raspberry Pi driven RGB LED 
matrix. Currently supports 64x32 boards only.

### Shout-out (Credit)
This project was inspired by the [mld-led-scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). Go check it out and try it on your board, even if you are not a baseball fan, it's amazing.
I also used this [nhlscoreboard repo](https://github.com/quarterturn/nhlscoreboard) as a guide at the very beginning as I was learning python.

## Features (V 0.1.0)

### Live game 
Display the live score in near real time (refresh every minute) of a 
select game (set in the config file). If one of the team score a goal, 
a goal animation (.gif) is played.

### Game day
If your team has a game scheduled, The screen will display a preview 
screen of the game.

### Off day
Display a message to announce the sad news.

## Installation
### Hardware Assembly
While writing this README page, I realized that the mlb-led-scoreboard guys made a great wiki page to cover the hardware part of the project. 
[See the mlb-led-scoreboard wiki page.](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki)

### Software Installation
#### Time Zones
Before you start installing anything, make sure your raspberry pi is set to your local time zone. Usually, you do so when you install Raspian, but if you think you skipped that part, you can change it by running `sudo raspi-config`

#### Requirements
You need Git for cloning this repo and PIP for installing the scoreboard software.
```
sudo apt-get update
sudo apt-get install git python-pip
```

#### Installing the NHL scoreboard software
This installation process might take some time because it will install all the dependencies listed below.

```
git clone --recursive https://github.com/riffnshred/nhl-led-scoreboard
cd nhl-led-scoreboard/
sudo ./install.sh
```
[rpi-rgb-led-matrix ](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building): The open-source library that allows the Raspberry Pi to render on the LED matrix.

[pytz](http://pytz.sourceforge.net/), [tzlocal](https://github.com/regebro/tzlocal): Timezone libraries. These allow the scoreboard to convert times to your local timezone.

## Disclaimer
This project use NHL's logo for information purposes only. I DO NOT own these logos.