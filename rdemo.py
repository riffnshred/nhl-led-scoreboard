import requests

r = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?date=2018-01-09')


data = r.json()
dates = data['dates'][0]
games = dates['totalGames']

print(games)
