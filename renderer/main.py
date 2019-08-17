from renderer.scoreboard_renderer import scoreboard
import time
import sys

print('NHL Scoreboard V0.01')
print('Gathering nhl data')


def renderer(data):
    try:
        print("Press CTRL-C to stop.")
        c = 0
        while True:

            time.sleep(10)
            c += 1
            print(c)

    except KeyboardInterrupt:
        sys.exit(0)
