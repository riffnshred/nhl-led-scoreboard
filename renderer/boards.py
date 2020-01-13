"""
Object

A Board is simply a display object with specific parameters made to be shown on screen.

Ex of parameters:


    Time stamp: The time the board appeared on screen/beginning of the rotation cycle. Used to calculate
                the timing between each rotation. Reset at end of rotation.

    Data: The Data to be displayed

    Layout: The layout information to position the data on the board (From 64x32_config.json loaded in data section)

    Fonts: The fonts used to show the data. (should be already loaded at boot and only selected here)

    Layers: Not all data can be displayed so we can split them on different layers and rotate through them
            or show specific ones at specific time or triggers.

            Ex 1 : Show Standings on 32x32 screen is a bit tight, so we can put the Points on one layer and
                   and the Win / Lost Stats on the other.

            Ex 2 : Showing the Time remaining to a power play on the Scoreboard board. Rotate between showing
                   the score and the power play information.

    Triggers: Can have as many as needed for the specific board. This is bool elements that can affect the
              state of the board.

            Ex 1 : If the intermission end and the current displayed board is not done showing the data, we can
                   add a trigger that if True, it will get get out of the board and get back to showing the
                   main scoreboard.
"""

class Board:
    def __init__(self):
        pass
