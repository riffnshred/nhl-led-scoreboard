# NHL-LED-scoreboard
![scoreboard demo](assets/images/scoreboard.jpg)

## Features (Beta V 1.0.0)

### State
Depending on the situation, the scoreboard will operate in different state. For exemple, If your team is off today, the
scoreboard we be in the "Offday" State. This allows to show specific boards (see Boards) depending on the state of the unit.

* **Scheduled** : When one of you preferred team has a game scheduled on the current day, the scoreboard will rotate through
a list of board set by the user in the config file.

* **Live game** : Display the live score in near real time of your favorite game. If one of the team score a goal, 
a goal animation (.gif) is played.

* **Intermission** : Between periods, the scoreboard will rotate through a list of board set 
for the intermission state by the user in the config file.

* **Post-game** : Once the game is over, the scoreboard will rotate through a list of board set 
for the Post-game state by the user in the config file.

### New Board System
The board system allow the user to choose what to display depending on the state of the scoreboard.
For exemple: While the game I'm watch is in the intermission state, I like to see the score ticker, which show the score 
of the other games.

There is currently three different boards available:
* **Score Ticker**: A carousel that cycle through the games of the day. 
* **Team Summary**: Display your preferred team's summary. It display their standing record, the result of their previous game
and the next game on their schedule.
* **Standings**: Display the standings either by conference or by division. The Wildcard is a work in progress and will be 
available soon.

The board system also allow to easily integrate new features. For example, if you want to have a clock displayed during the day
along with other boards, or if you wish one of the existing board would show something different, you can make your 
own and integrate it without touching the main software. I strongly suggest you play around with the python examples in 
the [rpi-rgb-led-matrix ](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building) to learn 
how to display anything on the matrix.

More will come soon with playoff related features

### Dimmer
The scoreboard now has a dimmer function. The scoreboard will change it's brightness at sunrise and sunset. If you have
a [TSL2561](https://www.adafruit.com/product/439) light sensor installed on your raspberry pi, you can configure the scoreboard
to use it to adjust the brightness.

### Network Indicator
If your scoreboard has trouble communicating with the API due to poor wifi or internet connection, It will display
a red bar at the bottom of the screen. Once the connection is back, the red bar will disappear.  

### Time and data accuracy
For this version, the scoreboard refresh the data at a faster rate (15 seconds by default, don't go faster then 10). This does not change the fact
that the data from the API is refreshed every minute. The faster refresh rate allow to catch the new data from the API faster.

Syncing the scoreboard with a TV Broadcast is, to my knowledge, impossible. The delay between the actual game and the TV 
broadcast is different depending on where you are in relation to the game's location. This also mean that you will 
definitely see the goal animation before it happens on TV. I'm working on this issue and looking to find a solution to implement
a delay.

## Installation
### Hardware Assembly
While writing this README page, I realized that the mlb-led-scoreboard guys made a great wiki page to cover the hardware part of the project. 
[See the mlb-led-scoreboard wiki page.](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki)

### Software Installation
#### Raspbian Buster Lite

To be sure that you have the best performance possible, this project require Raspbian Buster Lite.
this version does not have a GUI which allow the Pi to dedicate as much resource as possible to the scoreboard.

![scoreboard demo](assets/images/raspbian_buster_lite.png)

Fallow these instructions to install Raspbian Buster Lite on your Raspberry Pi and once you are up and running comeback to 
this page.

[Raspbian Buster Lite Installation](https://medium.com/@danidudas/install-raspbian-jessie-lite-and-setup-wi-fi-without-access-to-command-line-or-using-the-network-97f065af722e)

#### Time Zones
Before you start installing anything, make sure your raspberry pi is set to your local time zone. Usually, you do so when you install Raspian, but if you think you skipped that part, you can change it by running `sudo raspi-config`

#### Requirements
You need Git for cloning this repo and PIP for installing the scoreboard software.

Since version V 1.0.0 you need python 3.3 and up.
```
sudo apt-get update
sudo apt install git python3-pip
```

#### Installing the NHL scoreboard software
This installation process might take some time because it will install all the dependencies listed below.

```
git clone -b dev --recursive https://github.com/riffnshred/nhl-led-scoreboard
cd nhl-led-scoreboard/
sudo chmod +x install.sh
sudo ./scripts/install.sh
```
[rpi-rgb-led-matrix ](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building): The open-source library that allows the Raspberry Pi to render on the LED matrix.
[requests](https://requests.kennethreitz.org/en/master/): To call the API and manipulate the received data.


## Testing & Optimization (IMPORTANT)
If you have been using a Led matrix on a raspberry pi before and know how to run it properly skip this part. 

If you just bought your Led matrix and want to run this software right away, first thank you. Second, don't get to excited just yet.
Depending on your setup, you will need to configure the scoreboard using specific command flags when you run it.

Reference the [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix/). Check out the section that uses the python bindings and run some of their examples on your screen. For sure you will face some issues at first, but don't worry, more than likely there's a solution you can find in their troubleshooting section.
Once you found out how to make it run smoothly, come back here and do what's next.

### Adafruit HAT/bonnet
If you are using either a raspberry Zero, 3B+, 3A+ and 4B with an Adafruit HAT or Bonnet, here's what I did to run my board properly.

* Do the hardware mod found in the [Improving flicker section ](https://github.com/hzeller/rpi-rgb-led-matrix#improving-flicker).
* Disable the on-board sound. You can find how to do it from the [Troubleshooting sections](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting)
* From the same section, run the command that remove the bluetooth firmware, Unless you use any bluetooth device with your Pi.

Finally, here's the command I use. 
```
sudo python3 main.py --led-gpio-mapping=adafruit-hat-pwm --led-brightness=60 --led-slowdown-gpio=2
```

## Usage
First thing first, Using Open the config.json file from the root folder to configure your scoreboard.

### Modes
These are options to set the scoreboard to run in certain mode. This is where you enable the live game mode
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

### States
If the live mode is enabled, the scoreboard will go through different states depending on the current situation.
For each state, you can define which of the available board you want to scoreboard to show. For exemple, if one of my preferred
team has a game scheduled on the current day, during the day, the scoreboard will be in the `scheduled` state. I personally like
to have all the data possible shown during the day so I'll set the 
| Settings                                            | Type  | Parameters                                    | Description                                               |
|-----------------------------------------------------|-------|-----------------------------------------------|-----------------------------------------------------------|
| `off_day`, `scheduled`, `intermission`, `post_game` | Array | `["scoreticker", team_summary", "standings"]` | List of preferred boards to show for each specific state. |

### Boards
Boards are essentially like pages on a website. Each show something specific and the using can decide which board to display
at depending of the state of the scoreboard. Currently there is only three boards available:

* **Score Ticker**: This is basally like the generic score ticker you see during a game on TV of sports news showing the 
result or the status of the other games in the league. 

* **Standings**: Self explanatory, it shows the current standings. Currently you can choose between showing standings by conference or by divisions. Wildcard standings are coming soon.
* **Team Summary**: Show a summary of your preferred teams. It includes data like standing record, Result of the previous game and the next scheduled game.

| Boards        | Settings                   | Type | Parameters      | Description                                                                                       |  |  |  |
|---------------|----------------------------|------|-----------------|---------------------------------------------------------------------------------------------------|--|--|--|
| `scoreticker` | `preferred_teams_only`     | Bool | `true`, `false` | Choose between showing all the games of the day or just the ones your preferred teams are playing |  |  |  |
|               | `rotation_rate`            | INT  | `5`             | Duration at witch each games are shown on screen.                                                 |  |  |  |
| `standings`   | `preferred_standings_only` | Bool | `true`, `false` | Choose between showing all the standings or only the the preferred division and conference.       |  |  |  |




```
{
	"debug": true,                          
	"live_mode": true,                      
	"preferences": {
		"live_game_refresh_rate": 15,
		"end_of_day": "12:00",
		"teams": [
			"Canadiens",
			"Blackhawks",
			"Avalanche"
		],
		"standing_type": "conference",
		"divisions": "central",
		"conference": "eastern",
	},
	"boards": {
		"off_day": [
			"scoreticker",
			"team_summary",
			"standings"
		],
		"scheduled": [
			"scoreticker",
			"team_summary",
			"standings"
		],
		"intermission": [
			"scoreticker"
		],
		"post_game": [
			"scoreticker"
		],
		"scoreticker": {
			"preferred_teams_only": false,
			"rotation_rate": 5
		},
		"standings": {
			"preferred_standings_only": false
		}
	}
}

```

### Shout-out (Credit)
This project was inspired by the [mlb-led-scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). Go check it out and try it on your board, even if you are not a baseball fan, it's amazing.
I also used this [nhlscoreboard repo](https://github.com/quarterturn/nhlscoreboard) as a guide at the very beginning as I was learning python.

## Licensing
This project use the GNU Public License. If you intend to sell these, the code must remain open source.