# NHL-LED-scoreboard
![scoreboard demo](assets/images/scoreboard.jpg)

## Support and community
We have a nice community growing every day on discord. If you need help 
or you are curious about the development of the project, come join us by clicking on this button.

[![discord button](assets/images/discord_button.png)](https://discord.gg/CWa5CzK)

Want to help me turn coffee into features? Or just want to contribute
for my work? 

<a href="https://www.buymeacoffee.com/MgDa5sr" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/black_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

## Requirements
Since version V1.0.0 you need python 3.3 and up.

## Table of Contents
  - [Features](#features)
    - [States](#states)
    - [New Board System](#new-board-system)
    - [Goal animation](#goal-animation)
    - [Dimmer](#dimmer)
    - [Indicators](#indicators)
  - [Time and data accuracy](#time-and-data-accuracy)
  - [Installation](#installation)
    - [Hardware Assembly](#hardware-assembly)
      - [Installing and configuring a button.](#installing-and-configuring-a-button)
  - [Usage](#usage)
    - [Method 1 Using Supervisor](#method-1-using-supervisor)
    - [Method 2 Using Terminal Multiplexer](#method-2-using-terminal-multiplexer)
    - [Terminal Mode](#terminal-mode)
  - [Shout-out](#shout-out)
  - [Licensing](#licensing)
  
## Tutorials from other source
>"I followed instructions from somewhere else and I'm having issues"

This project is new and is in constant evolution. Please read the documentation and instructions to install and run this software provided here. 

## Features

### States
Depending on the situation, the scoreboard will operate in a different state. For example, If your team is off today, the scoreboard will be in the "Offday" State. This allows showing specific boards (see Boards) depending on the state of the unit.

-   **Offday** : Self explanatory, if anyteam in your preferred team list has no scheduled game during the current day, it will fall in this state. If you set the `Live mode` to `False` in the configuration file, the scoreboard will stay in that state until you change it `True`.
-   **Scheduled**: When one of your preferred team has a game scheduled on the current day, the scoreboard will rotate through a list of boards set by the user in the config file.
-   **Live game**: Display the live score in near real-time of your favorite game. If one of the team scores a goal, a goal animation (.gif) is played.
-   **Intermission**: Between periods, the scoreboard will rotate through a list of boards set for the intermission state by the user in the config file.
-   **Post-game**: Once the game is over, the scoreboard will rotate through a list of boards set for the Post-game state by the user in the config file.

### Board System
<img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/boards_scoreticker.png"> <img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/boards_team_summary.png"> <img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/board_standings.png"> <img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/clock.png">

The board system allows the user to choose what to display depending on the state of the scoreboard. For example: While the game I'm watching is in the intermission state, I like to see the score ticker, which is showing the score of the other games.

There are currently three different boards available:

-   **Score Ticker**: A carousel that cycles through the games of the day.
-   **Series Ticker (Available during the playoff only)**: A carousel that cycles through the Series of an ongoing round of Playoff.
-   **Team Summary**: Display your preferred team's summary. It displays their standing record, the result of their previous game and the next game on their schedule.
-   **Standings**: Display the standings either by conference or by division. The Wildcard is currently not available, due to the NHL API not providing the info, this will probably be back for next season.
-   **Clock**: a basic clock. (***NEW***: Now with the option to show basic weather information and weather alert. More details [here](https://github.com/riffnshred/nhl-led-scoreboard/tree/beta/src/api/weather))
-   **Weather**: Display weather information and also provide weather alerts. 
-   **Covid-19**: Show the number of cases, deaths and recovered cases of the covid-19 virus in real time (API updates about every 15 min).

The board system also allows to easily integrate new features. For example, if you want to have a clock displayed during the day along with other boards, or if you wish one of the existing boards would show something different, you can make your own and integrate it without touching the main software. I strongly suggest you play around with the python examples in the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building) to learn how to display anything on the matrix.

More will come soon with playoff related features and more. **If you have any suggestion, open an issue and come chat on discord**. 

### Goal animation
<img  width="400" src="https://github.com/riffnshred/image_bank/blob/master/nhl-led-scoreboard/documentation/goal_light_animation.png">
When ever a team in the main event score a goal, a goal light animation is played.
Soon you will have to option to set the animation for your favorite team only or play a different animation for
the opposing team.

### Dimmer
The scoreboard now has a dimmer function. The scoreboard will change its brightness at sunrise and sunset. If you have
a [TSL2591](https://www.adafruit.com/product/1980) light sensor installed on your raspberry pi, you can configure the scoreboard
to use it to adjust the brightness.

### Indicators
Because of its size, I programmed some indicators to display more information without filling up the screen and create an information overload issue. Please read the [Indicators](https://github.com/riffnshred/nhl-led-scoreboard/wiki/Indicators) page in the Wiki section for more details.

<img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/indicators.png"> <img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/network_indicator.png"> <img  width="200" src="https://github.com/riffnshred/image_bank/blob/master/nhl-led-scoreboard/documentation/intermission_indicator.png"> <img  width="200" src="https://raw.githubusercontent.com/riffnshred/image_bank/master/nhl-led-scoreboard/documentation/end_of_game_indicator.png">

## Time and data accuracy
For this version, the scoreboard refreshes the data at a faster rate (15 seconds by default, don't go faster than 10). This does not change the fact that the data from the API is refreshed every minute. The faster refresh rate allows catching the new data from the API faster.

Syncing the scoreboard with a TV Broadcast is, to my knowledge, impossible. The delay between the actual game and the TV 
broadcast is different depending on where you are in relation to the game's location. This also means that you will see the goal animation before it happens on TV. I'm working on this issue and looking to find a solution to implement
a delay.

Also, it might happen the data shown on board might be wrong for a short time, even goals. That's because the API is drunk. If you see data that might be wrong, compare it to the nhl.com and see if it's different. 

## Installation

### Hardware Assembly
**IMPORTANT NOTE**: Even tho there are other ways to run an rgb led matrix, I only support for the Adafruit HAT and Adafruit Bonnet.
If you create an issue because you are having trouble running your setup and you are using something different, I will close it and tell you to buy the
appropriate parts or to check the [rpi-rgb-led-matrix ](https://github.com/hzeller/rpi-rgb-led-matrix) repo.

Please refer to the [Home page](https://github.com/riffnshred/nhl-led-scoreboard/wiki/Home) and [Hardware page](https://github.com/riffnshred/nhl-led-scoreboard/wiki/Hardware) in the wiki section. You will find everything you need to order and build your scoreboard.

#### Installing and configuring a button.
To install and configure a button, please refer the well writen and detailed documentation in the SBIO section here: 
[src/sbio/SBIO.md](https://github.com/riffnshred/nhl-led-scoreboard/blob/master/src/sbio/SBIO.md). 


## Usage
Once you are done optimizing your setup and configuring the software, you are ready to go.

Start by running your board and see if it runs properly. If you use the typical Pi 3b+ and HAT/Bonnet setup, here's the command I use.

If you've done the anti-flickering mod, change the `--led-gpio-mapping=adafruit-hat` for `--led-gpio-mapping=adafruit-hat-pwm`
```
sudo python3 src/main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2
```

Once you know it runs well, turn off your command prompt. **SURPRISE !!!** the screen stop! That's because the SSH connection is interrupted and so the 
python script stopped.

There are multiple ways to run the Scoreboard on it's own. I'm going to cover 2 ways. One that's a bit more hand's on, and the other will run the
board automatically (and even restart in case of a crash).

### Method 1 Using Supervisor
![supervisor](assets/images/supervisor.PNG)

[Supervisor](http://supervisord.org/) is a Process Control System. Once installed and configured it will run the scoreboard for you and restart it
in case of a crash. What's even better is that you can also control the board from your phone !!!!

To install Supervisor, run this installation command in your terminal.
```
sudo apt-get install supervisor
```

Once the process done, open the supervisor config file,
```
sudo nano /etc/supervisor/supervisord.conf
```
and add those two lines at the bottom of the file.
```
[inet_http_server]
port=*:9001
```
Close and save the file.
```
Press Control-x
Press y
Press [enter]
```

Now lets create a new file called scoreboard.conf into the conf.d directory of supervisor, by running this command,
```
sudo nano /etc/supervisor/conf.d/scoreboard.conf
```
In this new file copy and past these line.
```
[program:scoreboard]
command=[SCOREBOARD COMMAND]
directory=[LOCATION OF THE SCOREBOARD DIRECTORY]
autostart=true
autorestart=true
```
Than fill in the missing information. For the `command`, insert the command that worked for you when you tested the scoreboard. If
you used the same as mine then this line should look like, `command=sudo python3 src/main.py --led-gpio-mapping=adafruit-hat-pwm --led-brightness=60 --led-slowdown-gpio=2`.
Lastly, for the `directory`, insert the location of the scoreboard directory. It should be something like `/home/{user}/nhl-led-scoreboard`. If you use the base account "pi" then
the `{user}` will be `pi`.

Now, reboot the raspberry pi. It should run the scoreboard automatically. Open a browser and enter the ip address of your raspberry pi in the address bar
fallowing of `:9001`. It should look similar to this `192.168.2.19:9001`. You will see the supervisor dashboard with the scoreboard process running.
If you see the dashboard but no process, reboot the pi and refresh the page. 

You should be up and running now. From the supervison dashboard, you can control the process of the scoreboard (e.g start, restart, stop).

To troubleshoot the scoreboard using supervision, you can click on the name of the process to see the latest log of the scoreboard. This is really useful to know what the scoreboard
is doing in case of a problem.

### Method 2 Using Terminal Multiplexer
To make sure it keeps running you will need a Terminal Multiplexer like. [Screen](https://linuxize.com/post/how-to-use-linux-screen/).
This allows you to run the scoreboard manually in a terminal and 
To install Screen, run the fallowing in your terminal.
```
sudo apt install screen
```

Then start a screen session like so
```
screen
```

Now run the scoreboard. Once it's up and running do `Ctrl+a` then `d`. This will detach the screen session from your terminal. 
NOW ! close the terminal. VOILA !!! The scoreboard now runs on it's own.

To go back and stop the scoreboard, open your terminal again and ssh to your Pi. Once you are in, do `screen -r`. This will bring the screen session up on your terminal.
This is useful if the scoreboard stop working for some reason, you can find out the error it returns and uses that to find a solution.

### Terminal Mode

Maybe you want to debug, or you have a small screen nearby that you want to use instead. You can run this in the terminal using:

`sudo python3 src/main.py --terminal-mode=true`

Note:

* If you want to run this straight from a raspberry pi, you will need to install a GUI and a terminal emulator that has all the colors
* If you are using a touchscreen instead of an HDMI output, make sure the [proper drivers are installed](https://github.com/goodtft/LCD-show)


## Shout-out

First, these two for making this repo top notch and already working on future versions:

- [Josh Kay](https://github.com/joshkay)
- [Sean Ostermann](https://github.com/falkyre)


This project was inspired by the [mlb-led-scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). Go check it out and try it on your board, even if you are not a baseball fan, it's amazing.
I also used this [nhlscoreboard repo](https://github.com/quarterturn/nhlscoreboard) as a guide at the very beginning as I was learning python.

You all can thank [Drew Hynes](https://gitlab.com/dword4) for his hard work on documenting the free [nhl api](https://gitlab.com/dword4/nhlapi).

## Licensing
This project uses the GNU Public License. If you intend to sell these, the code must remain open source.
