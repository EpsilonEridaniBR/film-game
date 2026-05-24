import matplotlib.pyplot as plt
from game import GAME
from deck import DECK
import analyse

itt = "a"
path = "v0.1/" + itt + "/input.csv"

players = ["RED", "BLUE", "YELLOW", "GREEN",]# "CYAN", "MAGENTA"]
pType = "a" #automated

num_games = 1000
log = []
movies = []

for i in range(num_games):
    g = GAME()
    g.createPlayers(pType, players)
    g.setup(path)
    g.setFestCount(2)
    g.run()
    log.append(g.actionlog)
    movies = movies + g.movies

g.printLog()
# g.printMovies()

#for player in g.players:
    #print(player.table)


analyse.plotBalance(log)
movieStats = analyse.plotMovies(movies)
analyse.deck(g.deck)

plt.show()

print("DONE")