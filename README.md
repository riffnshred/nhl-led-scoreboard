# NHL-LED-scoreboard
![scoreboard demo](assets/images/scoreboard.jpg)

## Join our community
We have a nice community growing every day on discord. If you need help 
or you are curious about the development of the project, come join us by clicking on this button.

[![discord button](assets/images/discord_button.png)](https://discord.gg/CWa5CzK)

## Table of Contents
- [Features (Beta V 1.0.0)](#features--beta-v-100-)
  * [States](#states)
  * [New Board System](#new-board-system)
  * [Dimmer](#dimmer)
  * [Network Indicator](#network-indicator)
- [Time and data accuracy](#time-and-data-accuracy)
- [Installation](#installation)
  * [Hardware Assembly](#hardware-assembly)
  * [Software Installation](#software-installation)
    + [Raspbian Buster Lite](#raspbian-buster-lite)
    + [Time Zones](#time-zones)
    + [Requirements](#requirements)
    + [Installing the NHL scoreboard software](#installing-the-nhl-scoreboard-software)
- [Testing & Optimization (IMPORTANT)](#testing---optimization--important-)
  * [Flags](#flags)
  * [Best Performance (Almost zero flicker)](#best-performance--almost-zero-flicker-)
- [Configuration](#configuration)
  * [Modes](#modes)
  * [Preferences](#preferences)
  * [Teams](#teams)
  * [States](#states-1)
  * [Boards](#boards)
  * [Dimmer](#dimmer-1)
  * [Usage](#usage)
- [Shout-out (Credit)](#shout-out--credit-)
- [Licensing](#licensing)
  


## Features (Beta V 1.0.0)

### States
Depending on the situation, the scoreboard will operate in a different state. For example, If your team is off today, the scoreboard will be in the "Offday" State. This allows showing specific boards (see Boards) depending on the state of the unit.

-   **Scheduled**: When one of your preferred team has a game scheduled on the current day, the scoreboard will rotate through a list of boards set by the user in the config file.
-   **Live game**: Display the live score in near real-time of your favorite game. If one of the team scores a goal, a goal animation (.gif) is played.
-   **Intermission**: Between periods, the scoreboard will rotate through a list of boards set for the intermission state by the user in the config file.
-   **Post-game**: Once the game is over, the scoreboard will rotate through a list of boards set for the Post-game state by the user in the config file.

### New Board System
The board system allows the user to choose what to display depending on the state of the scoreboard. For example: While the game I'm watching is in the intermission state, I like to see the score ticker, which is showing the score of the other games.

There are currently three different boards available:

-   **Score Ticker**: A carousel that cycles through the games of the day.
-   **Team Summary**: Display your preferred team's summary. It displays their standing record, the result of their previous game and the next game on their schedule.
-   **Standings**: Display the standings either by conference or by division. The Wildcard is a work in progress and will be available soon.

The board system also allows to easily integrate new features. For example, if you want to have a clock displayed during the day along with other boards, or if you wish one of the existing boards would show something different, you can make your own and integrate it without touching the main software. I strongly suggest you play around with the python examples in the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building) to learn how to display anything on the matrix.

More will come soon with playoff related features

### Dimmer
The scoreboard now has a dimmer function. The scoreboard will change its brightness at sunrise and sunset. If you have
a [TSL2591](https://www.adafruit.com/product/1980) light sensor installed on your raspberry pi, you can configure the scoreboard
to use it to adjust the brightness.

### Network Indicator
If your scoreboard has trouble communicating with the API due to poor wifi or internet connection, It will display
a red bar at the bottom of the screen. Once the connection is back, the red bar will disappear.  

## Time and data accuracy
For this version, the scoreboard refreshes the data at a faster rate (15 seconds by default, don't go faster than 10). This does not change the fact
that the data from the API is refreshed every minute. The faster refresh rate allows catching the new data from the API faster.

Syncing the scoreboard with a TV Broadcast is, to my knowledge, impossible. The delay between the actual game and the TV 
broadcast is different depending on where you are in relation to the game's location. This also means that you will see the goal animation before it happens on TV. I'm working on this issue and looking to find a solution to implement
a delay.

## Installation
### Hardware Assembly
**IMPORTANT NOTE**: Even tho there are other ways to run an rgb led matrix, I only support for the Adafruit HAT and Adafruit Bonnet.
If you create an issue because you are having trouble running your setup, I will close it and tell you to buy the
appropriate parts.

While writing this README page, I realized that the mlb-led-scoreboard guys made a great wiki page to cover the hardware part of the project. 
[See the mlb-led-scoreboard wiki page.](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki)

### Software Installation
#### Raspbian Buster Lite

To be sure that you have the best performance possible, this project requires Raspbian Buster Lite.
This version does not have a GUI which allows the Pi to dedicate as much resource as possible to the scoreboard.

![scoreboard demo](assets/images/raspbian_buster_lite.png)

Follow these instructions to install Raspbian Buster Lite on your Raspberry Pi and once you are up and running comeback to 
this page.

[Raspbian Buster Lite Installation](https://medium.com/@danidudas/install-raspbian-jessie-lite-and-setup-wi-fi-without-access-to-command-line-or-using-the-network-97f065af722e)

#### Time Zones
Before you start installing anything, make sure your raspberry pi is set to your local time zone. Usually, you do so when you install Raspian, but if you think you skipped that part, you can change it by running `sudo raspi-config`

#### Requirements
You need Git to clone this repo and PIP3 for installing the scoreboard software.

Since version V 1.0.0 you need python 3.3 and up.
```
sudo apt-get update
sudo apt install git python3-pip
```

#### Installing the NHL scoreboard software
This installation process might take some time because it will install all the dependencies listed below.

```
git clone -b beta --recursive https://github.com/riffnshred/nhl-led-scoreboard
cd nhl-led-scoreboard/
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

[rpi-rgb-led-matrix ](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building): The open-source library that allows the Raspberry Pi to render on the LED matrix.
[requests](https://requests.kennethreitz.org/en/master/): To call the API and manipulate the received data.


## Testing & Optimization (IMPORTANT)
If you have been using a Led matrix on a raspberry pi before and know how to run it properly skip this part. 

If you just bought your Led matrix and want to run this software right away, first thank you. Second, don't get too excited just yet.
Depending on your setup, you will need to configure the scoreboard using specific command flags when you run it.

To do so, start by disabling the audio of the raspberry pi (this is a must to run the led matrix properly).
From the root of the pi open the boot config file like so.
```
sudo nano /boot/config.txt
```

Find `dtparam=audio=on` and change it to `dtparam=audio=off`.

Save and close the file like so
```
Press Control-x
Press y
Press [enter]
```
reboot the pi
```
sudo reboot now
```

Now let's show something on the screen. Get to the matrix submodule and run some samples.

```
cd nhl-led-scoreboard/submodules/matrix/bindings/python/samples
sudo python3 runtext.py --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat-pwm --led-brightness=60
```
You should see "Hello World" scroll on screen.


Reference the [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix/). Check out the section that uses the python bindings and run some of their examples on your screen. For sure you will face some issues at first, but don't worry, more than likely there's a solution you can find in their troubleshooting section.
Once you found out how to make it run smoothly, come back here and do what's next.

### Flags
This is a list of Flags you can use to optimize your screen's performance. For more details check out the [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix/).

```
--led-rows                Display rows. 16 for 16x32, 32 for 32x32 and 64x32. (Default: 32)
--led-cols                Panel columns. Typically 32 or 64. (Default: 32)
--led-chain               Daisy-chained boards. (Default: 1)
--led-parallel            For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)
--led-pwm-bits            Bits used for PWM. Range 1..11. (Default: 11)
--led-brightness          Sets brightness level. Range: 1..100. (Default: 100)
--led-gpio-mapping        Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm
--led-scan-mode           Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)
--led-pwm-lsb-nanosecond  Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)
--led-show-refresh        Shows the current refresh rate of the LED panel.
--led-slowdown-gpio       Slow down writing to GPIO. Range: 0..4. (Default: 1)
--led-no-hardware-pulse   Don't use hardware pin-pulse generation.
--led-rgb-sequence        Switch if your matrix has led colors swapped. (Default: RGB)
--led-pixel-mapper        Apply pixel mappers. e.g Rotate:90, U-mapper
--led-row-addr-type       0 = default; 1 = AB-addressed panels. (Default: 0)
--led-multiplexing        Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; 5 = ZnMirrorZStripe; 6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)
```

### Best Performance (Almost zero flicker)
Using either a raspberry Zero, 3B+, 3A+ and 4B with an Adafruit HAT or Bonnet, here's what I did to run my board properly.

-   Do the hardware mod found in the [Improving flicker section](https://github.com/hzeller/rpi-rgb-led-matrix#improving-flicker).
-   Disable the onboard sound. You can find how to do it from the [Troubleshooting sections](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting)
-   From the same section, run the command that removes the Bluetooth firmware, Unless you use any Bluetooth device with your Pi.

Finally, these are the flag I use.

```
--led-gpio-mapping=adafruit-hat-pwm --led-brightness=60 --led-slowdown-gpio=2
```

## Configuration
First thing first, Open the config.json file from the config directory to configure your scoreboard.

### Modes
These are options to set the scoreboard to run in a certain mode. This is where you enable the live game mode
while will show the scoreboard of your favorite game when it's live.
| Settings    | Type | Parameters  | Description                                                           |
|-------------|------|-------------|-----------------------------------------------------------------------|
| `debug`     | Bool | true, false | Enable the debug mode which show on your console what the scoreboard  |
| `live_mode` | Bool | true, false | Enable the live mode which show live game data of your favorite team. |

### Preferences
All the data related options. 
| Settings                 | Type   | Parameters                                       | Description                                                                                                                                                                          |
|--------------------------|--------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `live_game_refresh_rate` | INT    | `15`                                             | The rate at which a live game will call the NHL API to catch the new data. Do not go under 10 seconds as it's pointless and will affect your scoreboard performance.(Default 15 sec) |
| `end_of_day`             | String | `"12:00"`                                        | A 24-hour time you wish to consider the end of the previous day before starting to display the current day's games.                                                                  |
| `teams`                  | Array  | `["Canadiens", Blackhawks", "Avalanche"]`        | List of preferred teams. First one in the list is considered the favorite. If left empty, the scoreboard will be in "offday" mode                                                    |
| `standing_type`          | String | `conference`, `division`                         | Option to choose the type of standings to display. `conference` if set by default.                                                                                                   |
| `divisions`              | String | `atlantic`, `metropolitan`, `central`, `pacific` | Your preferred division                                                                                                                                                              |
| `conference`             | String | `eastern`, `western`                             | Your preferred conference                                                                                                                                                            |

### Teams
For the `teams` parameters, only put the team's name. You can copy and paste your team's name from this table.

| Team names     | Team names  |
|----------------|-------------|
| `Avalanche`    | `Kings`     |
| `Blackhawks`   | `Knights`   |
| `Blues`        | `Leafs`     |
| `Blue Jackets` | `Lightning` |
| `Bruins`       | `Oilers`    |
| `Canadiens`    | `Panthers`  |
| `Canucks`      | `Penguins`  |
| `Capitals`     | `Predators` |
| `Coyotes`      | `Rangers`   |
| `Devils`       | `Red Wings` |
| `Ducks`        | `Sabres`    |
| `Flames`       | `Senators`  |
| `Flyers`       | `Sharks`    |
| `Hurricanes`   | `Stars`     |
| `Islanders`    | `Wild`      |
| `Jets`         |             |


### States
If the live mode is enabled, the scoreboard will go through different states depending on the current situation.
For each state, you can define which of the available board you want the scoreboard to show. For example, if one of my preferred
team has a game scheduled on the current day, during the day, the scoreboard will be in the `scheduled` state. I personally like
to have all the data possible shown during the day so I'll set the all the boards in the `scheduled` setting.

| Settings                                            | Type  | Parameters                                    | Description                                               |
|-----------------------------------------------------|-------|-----------------------------------------------|-----------------------------------------------------------|
| `off_day`, `scheduled`, `intermission`, `post_game` | Array | `["scoreticker", team_summary", "standings"]` | List of preferred boards to show for each specific state. |

### Boards
Boards are essentially like pages on a website. Each of them shows something specific and the user can decide which board to display

depending on the state of the scoreboard. Currently, there are only three boards available:

-   **Score Ticker**: This is basally like the generic score ticker you see during a game on TV of sports news showing the
-   result or the status of the other games in the league.
-   **Standings**: Self-explanatory, it shows the current standings. Currently, you can choose between showing standings by conference or by divisions. Wildcard standings are coming soon.
-   **Team Summary**: Show a summary of your preferred teams. It includes data like standing record, Result of the previous game and the next scheduled game.

| Boards        | Settings                   | Type | Parameters      | Description                                                                                       |
|---------------|----------------------------|------|-----------------|---------------------------------------------------------------------------------------------------|
| `scoreticker` | `preferred_teams_only`     | Bool | `true`, `false` | Choose between showing all the games of the day or just the ones your preferred teams are playing |
|               | `rotation_rate`            | INT  | `5`             | Duration at witch each games are shown on screen.                                                 |
| `standings`   | `preferred_standings_only` | Bool | `true`, `false` | Choose between showing all the standings or only the the preferred division and conference.       |


### Dimmer
The scoreboard can adjust the brightness of the matrix will running using the Dimmer function. By default, if enabled, 
the scoreboard software will detect your location using your IP address and will calculate the when the sun rise and the sun set.
It will then use these moments to change the brightness of the screen depending on the parameters set in the config.

If you install the [TSL2591](https://www.adafruit.com/product/1980) lux sensor, you can tell the scoreboard to use that to
control the brightness instead.

| Settings             | Type   | Parameters                 | Description                                                                                                                                                                                                                                                                                      |
|----------------------|--------|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `enabled`            | Bool   | `true`, `false`            | Enable the dimmer or not                                                                                                                                                                                                                                                                         |
| `source`             | String | `"hardware"`, `"software"` | Select the source that controle the dimmer. If set to `"software"`, the scoreboard will find your latitude and longitude based on your IP address. If an adafruit TSL2591 light sensor is connected to the Pi, you can set the source to `"hardware"` and let the sensor control the brightness. |
| `light_level_lux`    | INT    | `400`                      | This is the value you want the light sensor to start changing the brightness at                                                                                                                                                                                                                  |
| `frequency`          | INT    | `5`                        | Frequency at which the scoreboard will look if it needs to change the brightness                                                                                                                                                                                                                 |
| `mode`               | String | `"always"`, `"offday"`     | Mode at which the dimmer will operate. If set at `"always"`, the dimmer will operate at all time. at `"offday"`, it will operate only when your preferred teams don't play any games.                                                                                                            |
| `sunset_brightness`  | INT    | `10`                       | The brightness level (between 5 and 100)  you want when it's night.                                                                                                                                                                                                                              |
| `sunrise_brightness` | INT    | `60`                       | The brightness level (between 5 and 100)  you want during the day.                                                                                                                                                                                                                               |


### Usage
Once you are done optimizing your setup and configuring the software, you are ready to go.

Start by running your board and see if it runs properly. If you use the typical Pi 3b+ and HAT/Bonnet setup, here's the command I use.

```
sudo python3 src/main.py --led-gpio-mapping=adafruit-hat-pwm --led-brightness=60 --led-slowdown-gpio=2
```

Once you know it runs well, turn off your command prompt. **SURPRISE !!!** the screen stop! That's because the SSH connection is interrupted and so the 
python script stopped. 

To make sure it keeps running you will need a Terminal Multiplexer like. [Screen](https://linuxize.com/post/how-to-use-linux-screen/)

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

## Shout-out (Credit)
This project was inspired by the [mlb-led-scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). Go check it out and try it on your board, even if you are not a baseball fan, it's amazing.
I also used this [nhlscoreboard repo](https://github.com/quarterturn/nhlscoreboard) as a guide at the very beginning as I was learning python.

## Licensing
This project uses the GNU Public License. If you intend to sell these, the code must remain open source.
