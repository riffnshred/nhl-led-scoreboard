# The goal of the NHL led scoreboard

## DISCLAIMER

This is my first Open-source project. I never even contributed to an other project before. Until I showed my scoreboard on
Reddit and decided to share it, Github was just a backup server. Inevitably, this idea that I shared pulled me into the 
world of Open-source project. I'm still learning what this mean to this day. As an introvert, working 
with people on something that I intend to make for my self is challenging, yet exciting at the same time.

Even if this is a personal project, I want to turn it into something customizable so that the user can make his own 
personalized scoreboard. That's why I made the board system. If you have an idea like showing the weather during the day,
you can fork the repository and work on a weather board. If it looks and works great and we don't have something
similar already on the project, I will accept a pull request. Even if I don't accept your feature or idea into the project, 
if it's well made and I think someone else might enjoy it, I will advertise it in the Wiki page or the READ ME.


## TL;DR

### What this Project IS !
- A project meant for novice and those who are curious about making their first DIY electronic project. (Read more below)
- A desktop unit that display your favourite teams scoreboard and keeps you posted on whats going on in the hockey world.
- Aiming at 64x32 resolution matrix board but open to 32x32 , 64x64, and 128x32 intergration as long as it respect the 
design guide line.

### What it's NOT !
- An extension of what you are watching on TV. (Read Limitations below)
- Replace a full scoreboard (e.g showing who's on the ice, a detailed info of standings etc...)
- Not meant to show other sports data except if it's hockey related.

## Built for the fans AND the newbies.
One thing that's important for me is to keep the project as user friendly and accessible as possible. The target 
audience is basically anyone who loves hockey and just needed that extra push to do their first DIY project. 
The hardware is very easy to assemble without any knowledge of electronics and the reward is high if you just fallow the 
instruction. There for, any features added to this project must not require extra knowledge from the user (other then the basic from running a Pi) and needs to be properly documented.

## Limitations
Because of how the API works, there are some limitations and inconveniences. For instance, the API refresh itself every
minutes, so even if the scoreboard check the API at a set refresh rate (15 sec by default), the information will not change until
it catch the update.

An other inconvenient is that the live broadcast on TV/Radio/Internet has a random latency which can be between 30 sec to
a minutes (from what I experienced so far). Which means the scoreboard will show the information before it happens on the 
broadcast you are watching/listening. I'm working on a feature that adds a delay to the scoreboard, but that is not a done deal yet.

The other limitation is the screen size. Due too the 64x32 resolution, the amount of information we can show on screen is
limited. Obviously you can add multiple screen together and show even more information, but my goal is to keep the setup simple,
(single screen for now). I intend to develop some text scrolling and rotating functions along with the new features but keep in mind that it wont be
meant to display detailed information.


## Roadmap

### V1.x

Features:
- Brainstorm playoff features (need to make board draft and work on Playoff data)
- Off season features (Drafting)
- News ticker
- Events (Special dates like Draft, Trade Deadline, Season start and end.)
- Shootout screen (Show the shootout table.)

