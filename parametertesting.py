import matplotlib.pyplot as plt
import numpy as np
import csv
import analyse
from game import Game

def recordstats(dic, paraStr, arr):
    dic[paraStr + " MEAN"] = np.mean(arr)
    dic[paraStr + " STDev"] = np.std(arr)
    dic[paraStr + " MAX"] = np.max(arr)
    dic[paraStr + " MIN"] = np.min(arr)

itt = "a"
path = itt + "/input.csv"
savepath = itt + "/massanalysis.csv"

players = ["A","B","C","D","E","F","G","H","I","J","K","L"]

nogames = 1000
playercount = [2,3,4,6,8]
festivalcount = [1,2,3,4,5,6]
startingcash = [25,50,75,100,125,150]
startingcards = [2,3,4,6]

gamestates = []
records = []

for pcount in playercount:
    for fcount in festivalcount:
        for cash in startingcash:
            for cards in startingcards:
                gamestates.append([pcount, fcount, cash, cards])

for gamestate in gamestates:
    record = {
        "#players": gamestate[0],
        "#festivals": gamestate[1],
        "cash": gamestate[2],
        "cards": gamestate[3]
    }

    playing = players[0:record["#players"]]
    wins = {}
    winningbalances = []
    balancechanges = []
    actionsmade = []
    moviesmade = []

    for player in playing:
        wins[player] = 0

    for i in range(nogames):
        g = Game()
        g.createPlayers("a", playing)
        g.setup(path, record["cash"], record["#festivals"], record["cards"])
        g.run()

        [w, wb, ecs] = analyse.getWinner(g)
        wins[w] = wins[w]+1
        winningbalances.append(wb)

        for ec in ecs:
            balancechanges.append(ec - record["cash"])

        actionsmade.append(len(g.actionlog))
        moviesmade.append(len(g.movies))

    winperc = [val*100/nogames for val in list(wins.values())]
    recordstats(record, "WINNING %",winperc)    
    recordstats(record, "WINNING BALANCE", winningbalances)
    recordstats(record, "BALANCE CHANGES", balancechanges)
    recordstats(record, "ACTIONS TAKEN", actionsmade)
    recordstats(record, "MOVIES MADE", moviesmade)
    records.append(record)


with open(savepath, "w", newline='') as csvfile:
    csvwriter = csv.DictWriter(csvfile, record.keys())
    csvwriter.writeheader()
    csvwriter.writerows(records)

print("DONE")