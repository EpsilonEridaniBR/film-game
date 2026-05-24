import random
from movie import MOVIE

robobehav = ["random", "boring"]

class PLAYER:
    def __init__(self, name, robobool):
        self.name = name
        self.automated = robobool
        if self.automated:
            self.behaviour = robobehav[1]

    def __str__(self):
        return self.name

    def reset(self, cash):
        self.balance = cash
        self.hand = []
        self.table = {}
        self.movies = []

    def info(self):
        print(self.name)
        print("CURRENT BALANCE: " + str(self.balance) + "; MOVIES MADE: " + str(len(self.movies)))
        print("IN HAND")
        for i in range(len(self.hand)):
            print("[" + str(i) + "]: " + str(self.hand[i]))

    def bid(self, card, currentbid):
        bid = 0

        if self.automated:
            if self.behaviour == "boring":
                bid = card.avg
            elif self.behaviour == "random":
                bid = currentbid + random.randint(0,1)


        if bid < self.balance:
            return round(bid)
        else:
            return 0

    def addToTable(self, card, index):
        if card.cat not in self.table:
            self.table[card.cat] = [index]
        else:
            self.table[card.cat].append(index)

    def rebuildTable(self):
        self.table = {}
        for i in range(len(self.hand)):
            card = self.hand[i]
            self.addToTable(card, i)

    def giveCard(self, card):
        self.hand.append(card)
        index = len(self.hand) - 1
        self.addToTable(card, index)

    def removeCard(self, card):
        self.hand.remove(card)
        self.rebuildTable()

    def changeBalance(self, amount, negabool):
        self.balance = self.balance + (amount * ((-1)**negabool))
        if self.balance < 0:
            self.balance = 0

    def testMovie(self):
        mpackage = []
        if "SCRIPT" in self.table and "DIRECTOR" in self.table and "ACTOR" in self.table:
            scripts = self.table["SCRIPT"]
            noS = len(scripts)
            directors = self.table["DIRECTOR"]
            noD = len(directors)
            actors = self.table["ACTOR"]
            noA = len(actors)

            if noS*noD*noA > 0:
                mpackage = [self.hand[scripts[0]], self.hand[directors[0]], self.hand[actors[0]]]

        return mpackage

    def makeMovie(self, script, director, actor):
        movie = MOVIE(script, director, actor)
        self.removeCard(script)
        self.removeCard(director)
        self.removeCard(actor)

        movie.roll()
        movie.applyMods()

        self.movies.append(movie)
        return movie

    def playDebuff(self):
        if self.automated:
            card = self.hand[self.table["DEBUFF"][0]]
            self.removeCard(card)
            return card
        
    def playAction(self):
        if self.automated:
            card = self.hand[self.table["EVENT"][0]]
            self.removeCard(card)
            return card
