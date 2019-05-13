from nhlpy import game
import json

knights_vs_sharks = game.Game(2018030187)
my_json = knights_vs_sharks.all_stats()

print(json.dumps(my_json, indent=4, sort_keys=True))
