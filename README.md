# NHL-LED-scoreboard
![scoreboard demo](imgs/scoreboard.jpg)

Display NHL score of your favorite team on a Raspberry Pi driven RGB LED 
matrix. Currently supports 64x32 boards, but more to come in the near 
future.

## Current Features (V 1.0)

### Live game 
Display the live score in near real time (refresh every minute) of a 
select game (set in the config file). If one of the team score a goal, 
a goal animation (.gif) is played. 

### Game day
If your team has a game scheduled, The screen will display a preview 
screen of the game with both teams logo and the time the game start in
your time zone (make sure you configure your raspberry pi to your timezone). 


