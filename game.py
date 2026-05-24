import datetime
import random
from player import PLAYER
from deck import DECK
from card import CARD
from movie import MOVIE

class GAME:
    def __init__(self):
        self.actionlog = []
        self.timeOfGeneration = datetime.datetime.now()
        self.actionlog.append("Game Generated @ " + str(self.timeOfGeneration))

    def log(self, message: str):
        log: list = []
        log.append("TURN: ")
        log.append(self.turnNo)
        log.append("CARDS LEFT: " + str(self.deck.tpleng))
        log.append(message)
        log.append("CASH:")

        for player in self.players:
            log.append(player.balance)

        self.actionlog.append(log)

    def createPlayers(self, type: str, arr: list[str]):

        self.players: list[PLAYER] = []

        if type == "a":
            self.automated = 1
        else:
            self.automated = 0
        
        for name in arr:
            self.players.append(PLAYER(name, self.automated))

        self.noPlayers = len(self.players)

    def resetPlayers(self, cash: int):
        for player in self.players:
            player.reset(cash)

    def awardsVote(self):
        if self.automated:
            winner = self.players[random.randrange(0, self.noPlayers)]
            winner.changeBalance(10, 0)

    def newFest(self):

        if self.fest != self.deck.null:
            self.awardsVote()
            self.deck.fdisc.append(self.fest)

        self.fest = self.fest = self.deck.revFest()
        self.log("NEW FESTIVAL! - " + str(self.fest))
    
    def setup(self, path):
        self.turnNo = 0
        self.pIndex = 0
        self.deck = DECK()
        self.deck.build(path)
        self.deck.shuffle()
        
        self.resetPlayers(100)
        self.fest = self.deck.null
        self.debuff = self.deck.null
        self.movies: list[MOVIE] = []
        self.newFest()

        noCards = 6

        for i in range(noCards*self.noPlayers):
            card = self.deck.reveal()
            self.players[i%self.noPlayers].giveCard(card)

    def setFestCount(self, count: int):
        self.festCount = count
        self.endGame = 0

    def startEndGame(self):
        self.endGame = 1
        self.log("FESTIVALS ARE OVER - END GAME HAS STARTED")

    def bidding(self, card: CARD):
        bidders = self.players.copy()
        bindex = self.pIndex
        bid = 0

        while len(bidders) > 1:
            
            bindex = bindex+1
            bleng = len(bidders)

            if bindex >= bleng:
                bindex = 0

            bidder = bidders[bindex]
            newbid = bidder.bid(card, bid)

            if newbid > bid:
                bid = newbid
            else:
                bidders.remove(bidder)
                bindex = bindex-1

        bidders[0].giveCard(card)
        bidders[0].changeBalance(bid, 1)
        self.log(str(bidders[0]) + " bought " + str(card) + " for " + str(bid))

    def replaceDebuff(self, newDebuff):
        if self.debuff != self.deck.null:
            self.deck.discard.append(self.debuff)

        self.log(str(self.debuff) + " has been replaced by " + str(newDebuff))
        self.debuff = newDebuff

    def applyAction(self, card: CARD, activePlayer: PLAYER):
        name = card.name
        mods = card.modifiers
        keys = list(mods.keys())
        key = keys[0]
        val = mods[key]

        if name == "CASH INJECTION":
            balances = self.actionlog[-1][5:]
            poorest = self.players[balances.index(min(balances))]
            poorest.changeBalance(int(val[1:]), 0)
        elif name == "TAX SCANDAL":
            balances = self.actionlog[-1][5:]
            richest = self.players[balances.index(max(balances))]
            richest.changeBalance(int(val[1:]), 1)
        elif name == "POACH TALENT":
            if self.automated:
                victim = self.players[random.randrange(0, self.noPlayers)]
                noCards = len(victim.hand)
                if noCards > 0:
                    card = victim.hand[random.randrange(0, noCards)]
                    victim.removeCard(card)
                    activePlayer.giveCard(card)
        elif name == "STRIKE ACTION":
            for player in self.players:
                cost = round(player.balance * (int(val[1:])/100))
                player.changeBalance(cost, 1)


        self.log(str(card) + " applied action")

    def nextTurn(self):
        if self.deck.tpleng == 0:
            if not self.endGame:
                self.festCount = self.festCount - 1
                if self.festCount == 0:
                    self.startEndGame()
                else:
                    self.newFest()
                    self.deck.recycle()

        # initialise turn
        self.turnNo = self.turnNo + 1
        activePlayer = self.players[self.pIndex]

        if not self.endGame:

            activeCard = self.deck.reveal()
            

            if not self.automated:
                activeCard.info()

            # card actions
            # bid if needed
            if hasattr(activeCard, "dice"):
                self.bidding(activeCard)
            elif activeCard.cat == "DEBUFF":
                self.replaceDebuff(activeCard)
            elif activeCard.cat == "EVENT":
                self.applyAction(activeCard, activePlayer)
            else:
                self.log("SKIPPED " + str(activeCard))

        # play debuff
        if "DEBUFF" in activePlayer.table:
            card = activePlayer.playDebuff()
            if isinstance(card, CARD):
                self.log(str(activePlayer) + " has played " + str(card))
                self.replaceDebuff(card)

        # play action
        if "EVENT" in activePlayer.table:
            card = activePlayer.playAction()
            if isinstance(card, CARD):
                self.log(str(activePlayer) + " has played " + str(card))
                self.applyAction(card, activePlayer)

        # play movie
        if self.automated:
            mpackage = activePlayer.testMovie()
            if len(mpackage) == 3:
                movie = activePlayer.makeMovie(mpackage[0], mpackage[1], mpackage[2])
                movie.modify(self.fest.name)
                movie.modify(self.debuff.name)
                activePlayer.changeBalance(movie.value, 0)
                self.log(str(activePlayer) + " made " + str(movie) + " for " + str(movie.value))
                self.movies.append(movie)

        if self.pIndex == self.noPlayers - 1:
            self.pIndex = 0
        else:
            self.pIndex = self.pIndex + 1

    def run(self):

        while not self.endGame:
            self.nextTurn()

        for i in range(self.noPlayers):
            self.nextTurn()

    def printLog(self):
        for item in self.actionlog:
            print(item)
    
    def printMovies(self):
        for movie in self.movies:
            print([str(movie), movie.value])
            