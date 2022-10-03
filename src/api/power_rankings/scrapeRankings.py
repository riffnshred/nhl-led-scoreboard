import requests
from bs4 import BeautifulSoup
import json
url = "http://powerrankingsguru.com/nhl/team-power-rankings.php"
request = requests.get(url).text
soup = BeautifulSoup(request, "html.parser")

tr = soup.find_all("tr")
# print(tr)
# get the first table row and then the first span
span = tr[2].find_all("span")

print(span[0].string, "is the best team in the NHL")
rankings = {}
# print(tr[1].find_all("span"))
# get the second table row and then the tr with the class "col-text-center move move-col"
# td = tr[1].find_all("td")[3]
# print(td)
for i in range(32):
    td = tr[i + 1].find_all("td")[3].string
    last_week = 0
    if td == "-":
        last_week = i + 1
        # print(last_week)
        move = "No change"
    # else if td contains "↑" then cut off everything but the interger in the string
    elif td[0] == "↑":
        last_week = int(td[1:])
        # print(last_week)
        last_week = i + 1 + last_week
        # print(last_week)
        move = "Up"
    elif td[0] == "↓":
        last_week = int(td[1:])
        last_week = i + 1 - last_week
        move = "Down"
    print("#",i + 1, tr[i + 1].find_all("span")[1].string,"--- Last week rank:",last_week , f"({move})")    

    
    team = tr[i + 1].find_all("span")[1].string
    rank = i
    rankings[rank] = {"team": team, "last_week": last_week}

    
# convert the rankings to json with an indent of 2
# rankings_json = json.dumps(rankings, indent=2)
# print(rankings_json)
# print(rankings)