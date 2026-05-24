import datetime
import random
from player import Player
from deck import Deck
from card import Card, BiddableCard
from movie import Movie

class Game:
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

        self.players: list[Player] = []

        if type == "a":
            self.automated = 1
        else:
            self.automated = 0

        for name in arr:
            self.players.append(Player(name, self.automated))

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

    def setup(self, path: str):
        self.turnNo = 0
        self.pIndex = 0
        self.deck = Deck()
        self.deck.build(path)
        self.deck.shuffle()

        self.resetPlayers(25)
        self.fest = self.deck.null
        self.debuff = self.deck.null
        self.movies: list[Movie] = []
        self.lastBuyer: Player | None = None

        noCards = 6
        deal_cats = {"SCRIPT", "DIRECTOR", "ACTOR"}

        for i in range(noCards*self.noPlayers):
            card = self.deck.reveal_cat(deal_cats)
            self.players[i%self.noPlayers].giveCard(card)

        self.deck.shuffle()

    def activateFestival(self, card: Card):
        if self.fest != self.deck.null:
            self.awardsVote()
        self.fest = card
        self.log("NEW FESTIVAL! - " + str(self.fest))

    def setFestCount(self, count: int):
        self.festCount = count
        self.endGame = 0
        self.deck.addFestivals(count)
        self.newFest()

    def startEndGame(self):
        self.endGame = 1
        self.log("FESTIVALS ARE OVER - END GAME HAS STARTED")

    def bidding(self, card: BiddableCard):
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

        self.lastBuyer = bidders[0]
        bidders[0].giveCard(card)
        bidders[0].changeBalance(bid, 1)
        self.log(str(bidders[0]) + " bought " + str(card) + " for " + str(bid))

    def replaceDebuff(self, newDebuff):
        if self.debuff != self.deck.null:
            self.deck.discard.append(self.debuff)

        self.log(str(self.debuff) + " has been replaced by " + str(newDebuff))
        self.debuff = newDebuff

    # --- event handlers ---

    def _handle_cash_injection(self, card: Card, player: Player):
        amount = int(list(card.modifiers.values())[0][1:])
        poorest = min(self.players, key=lambda p: p.balance)
        poorest.changeBalance(amount, 0)
        return poorest.name, ""
    
    def _handle_tax_credit(self, card: Card, player: Player):
        amount = int(list(card.modifiers.values())[0][1:])
        if self.lastBuyer:
            self.lastBuyer.changeBalance(amount, 0)
            return self.lastBuyer.name, ""
        return None, ""

    def _handle_tax_scandal(self, card: Card, player: Player):
        richest = max(self.players, key=lambda p: p.balance)
        dice_roll = sum(random.randint(1, 8) for _ in range(3))
        richest.changeBalance(dice_roll, 1)
        return (dice_roll, richest.name), " - rolled " + str(dice_roll)

    def _handle_poach_talent(self, card: Card, player: Player):
        if self.automated:
            victim = self.players[random.randrange(0, self.noPlayers)]
            if victim.hand:
                stolen = victim.hand[random.randrange(0, len(victim.hand))]
                victim.removeCard(stolen)
                player.giveCard(stolen)
        return None, ""

    def _handle_strike_action(self, card: Card, player: Player):
        pct = int(list(card.modifiers.values())[0][1:])
        for p in self.players:
            cost = round(p.balance * (pct / 100))
            p.changeBalance(cost, 1)
        return None, ""

    def _handle_lifetime_achievement(self, card: Card, player: Player):
        # awarded to player who has released the most films
        if not self.movies:
            return None, ""
        amount = int(list(card.modifiers.values())[0][1:])
        winner = max(self.players, key=lambda p: len(p.movies))
        winner.changeBalance(amount, 0)
        return winner.name, ""

    def _handle_aarp_award(self, card: Card, player: Player):
        # awarded to player who has released the most films featuring a VETERAN director
        def veteran_count(p: Player):
            return sum(1 for m in p.movies if m.director.name == "VETERAN")
        if not any(veteran_count(p) > 0 for p in self.players):
            return None, ""
        amount = int(list(card.modifiers.values())[0][1:])
        winner = max(self.players, key=veteran_count)
        winner.changeBalance(amount, 0)
        return winner.name, ""

    def _handle_planted_pr_piece(self, card: Card, player: Player):
        # active player gets bonus and the current debuff is cleared
        amount = int(list(card.modifiers.values())[0][1:])
        player.changeBalance(amount, 0)
        if self.debuff != self.deck.null:
            self.deck.discard.append(self.debuff)
            self.debuff = self.deck.null
        return player.name, ""

    def _handle_tourism(self, card: Card, player: Player):
        # awarded to player who released the most recent movie
        amount = int(list(card.modifiers.values())[0][1:])
        if self.movies:
            last_movie = self.movies[-1]
            for p in self.players:
                if p.movies and p.movies[-1] is last_movie:
                    p.changeBalance(amount, 0)
                    return p.name, ""
        return None, ""

    def applyAction(self, card: Card, activePlayer: Player):
        handlers = {
            "CASH INJECTION":       self._handle_cash_injection,
            "TAX CREDIT":           self._handle_tax_credit,
            "TAX SCANDAL":          self._handle_tax_scandal,
            "POACH TALENT":         self._handle_poach_talent,
            "STRIKE ACTION":        self._handle_strike_action,
            "LIFETIME ACHIEVEMENT": self._handle_lifetime_achievement,
            "AARP AWARD":           self._handle_aarp_award,
            "PLANTED PR PIECE":     self._handle_planted_pr_piece,
            "TOURISM":              self._handle_tourism,
        }
        handler = handlers.get(card.name)
        result, log_suffix = handler(card, activePlayer) if handler else (None, "")
        self.log(str(card) + " applied action" + log_suffix)
        return result

    def nextTurn(self):
        if self.deck.tpleng == 0:
            if not self.endGame:
                self.startEndGame()

        self.turnNo = self.turnNo + 1
        activePlayer = self.players[self.pIndex]

        if not self.endGame:

            activeCard = self.deck.reveal()

            if not self.automated:
                activeCard.info()

            if isinstance(activeCard, BiddableCard):
                self.bidding(activeCard)
            elif activeCard.cat == "DEBUFF":
                self.replaceDebuff(activeCard)
            elif activeCard.cat == "EVENT":
                self.applyAction(activeCard, activePlayer)
            elif activeCard.cat == "FESTIVAL":
                self.activateFestival(activeCard)
            else:
                self.log("SKIPPED " + str(activeCard))

        # play debuff
        if "DEBUFF" in activePlayer.table:
            card = activePlayer.playDebuff()
            if isinstance(card, Card):
                self.log(str(activePlayer) + " has played " + str(card))
                self.replaceDebuff(card)

        # play action
        if "EVENT" in activePlayer.table:
            card = activePlayer.playAction()
            if isinstance(card, Card):
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
