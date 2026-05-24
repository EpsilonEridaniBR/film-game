import numpy as np
import matplotlib.pyplot as plt
from movie import Movie
from deck import Deck
from game import Game

colours = ['r', 'b', 'y', 'g', 'c', 'm']

def plotBalance(logs):

    for log in logs:
        fig = plt.figure

        turn = 0
        lastitem = log[-1]
        noPlayers = len(lastitem[5:])

        x = []
        y = []

        for i in range(noPlayers):
            y.append([])

        for i in range(len(log)):
            item = log[i]
            if isinstance(item, type(list())):
                tunrNo = item[1]
                if tunrNo > turn:
                    turn = tunrNo
                    x.append(tunrNo)
                    for j in range(noPlayers):
                        y[j].append(item[5+j])

        for i in range(noPlayers):
            plt.plot(x, y[i], colours[i])
                
def plotMovies(movielist: list[Movie]):

    fig = plt.figure()

    uniqueList = []
    xticks = []
    dictionary = {}
    stats = {}

    for movie in movielist:
        if str(movie) in dictionary:
            dictionary[str(movie)].append(movie.value)
        else:
            uniqueList.append(movie)
            xticks.append(str(movie))
            dictionary[str(movie)] = []
            dictionary[str(movie)].append(movie.value)

    for i in range(len(uniqueList)):
        movie = uniqueList[i]
        values = dictionary[str(movie)]

        #for value in values:
        #    plt.plot(i, value, ".", color=colours[i%len(colours)])

        moviestats = {
            "mean": np.mean(values),
            "std": np.std(values),
            "max": np.max(values),
            "min": np.min(values)
        }

        stats[str(movie)] = moviestats

        plt.plot([i, i], [moviestats["max"], moviestats["min"]], color=colours[i%len(colours)])
        plt.plot(i, moviestats["mean"], "o", color=colours[i%len(colours)])
        plt.plot(i, moviestats["mean"]+moviestats["std"], "^", color=colours[i%len(colours)])
        plt.plot(i, moviestats["mean"]-moviestats["std"], "v", color=colours[i%len(colours)])
        

    #plt.xticks(np.arange(len(xticks)), xticks, rotation='vertical')

    return stats

def deck(deck: Deck):
    fig = plt.figure()
    noCards = len(deck.deck)
    cats = list(deck.table.keys())
    rad = (2*np.pi)/noCards

    x = []
    y = []

    for i in range(noCards):
        xpos = np.sin(rad*i)
        x.append(xpos)
        ypos = np.cos(rad*i)
        y.append(ypos)
        
    for i in range(noCards):
        card = deck.deck[i]

        for mod in card.modifiers:
            if mod in deck.glossary:
                pairedIndex = deck.glossary[mod]
                value = card.modifiers[mod]
                sign = value[0]
                mag = int(value[1])
                w = 0.5*mag
                if sign == '+':
                    colour = 'g'
                else:
                    colour = 'r'   

                plt.plot([x[i], x[pairedIndex]], [y[i], y[pairedIndex]], color=colour, linewidth=w)         

    for i in range(noCards):
        card = deck.deck[i]
        r = card.qty
        c = colours[cats.index(card.cat)]
        plt.plot(x[i], y[i], "o", color=c)


def getWinner(game: Game):
    lastturn = game.actionlog[-1]
    endcash = lastturn[5:]
    winningBalance = max(endcash)
    winner = game.players[endcash.index(winningBalance)].name 
    return [winner, winningBalance, endcash]