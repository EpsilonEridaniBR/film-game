import csv
import random
from card import CARD

class DECK:
    def __init__(self):
        self.status = "UNDEFINED"
        self.deck = [] # list of all unqiue cards
        self.glossary = {}
        self.table = {} # dictionary the maps categories of cards to deck indecies

    def paircard(self, card: CARD, pairid: int, mod):
        # applies modifies to a pair of cards
        pairedcard = self.deck[pairid]
        card.attachModifier(pairedcard.name, mod)
        pairedcard.attachModifier(card.name, mod)

    def resetdeck(self):
        self.flist = [] # list of all festival cards (includes duplicates)
        self.fdisc = [] # list of all discarded festivals
        self.toplay= [] # list of all cards not currently discarded 
        self.discard = [] # list of all discarded cards

        for card in self.deck:
            for i in range(card.qty):
                if card.cat == "FESTIVAL":
                    self.flist.append(card)
                else:
                    self.toplay.append(card)

        self.flleng = len(self.flist)
        self.tpleng = len(self.toplay)

    def build(self, path):

        self.null = CARD("N/A", "NULL", "NULL", 0)

        with open(path, mode='r') as file:
            cards = csv.reader(file) # list of rows from passed through csv path
            for line in cards:
                index = int(line[0][-2:]) #index in deck +1 used to pair cards
                category = line[1]  # category e.g. "ACTOR"
                name = line[2] # unique refence name e.g. "SCREAM QUEEN"
                qty = int(line[3]) # number of duplicates

                # maps out self.table with unique categories and indecies
                if category not in self.table:
                    self.table[category] = [index]
                else:
                    self.table[category].append(index)

                # creates card object and appends to deck
                card = CARD(index, category, name, qty)
                self.deck.append(card)
                self.glossary[name] = len(self.deck) - 1

                # assigns card value
                val = line[4] 

                if val != "N/A":
                    card.assignVal(val)
                
                # assigns card modifiers
                modifiers = line[5:]
                noModPairs = int(len(modifiers)/2)

                for modindex in range(noModPairs):
                    pair = modifiers[modindex*2]
                    mod = modifiers[modindex*2+1]

                    if pair != "":
                        if pair in self.glossary:
                            self.paircard(card, self.glossary[pair], mod)
                        elif pair == "ALL SCRIPTS":
                            for sindex in self.table["SCRIPT"]:
                                self.paircard(card, sindex-1, mod)
                        else:
                            card.attachModifier(pair, mod)

            # populates sublists from complete deck
            self.resetdeck()

            self.size = self.tpleng + self.flleng
            for card in self.deck:
                if hasattr(card, "dice"):
                    card.calcProb(self.tpleng)

    def shuffle(self):
        random.shuffle(self.toplay)

    def reveal(self):
        if self.tpleng >= 1:
            card = self.toplay[0]
            self.discard.append(card)
            self.toplay.remove(card)
            self.tpleng = len(self.toplay)
            return card

    def reveal_cat(self, cats: set):
        for card in self.toplay:
            if card.cat in cats:
                self.discard.append(card)
                self.toplay.remove(card)
                self.tpleng = len(self.toplay)
                return card
                        
    def revFest(self):
        if self.flleng >= 1:
            festival = self.flist[random.randint(0, self.flleng-1)]
            self.fdisc.append(festival)
            self.flist.remove(festival)
            self.flleng = len(self.flist)
            return festival
        
    def addFestivals(self, n: int):
        selected = random.sample(self.flist, min(n, self.flleng))
        for fest in selected:
            self.flist.remove(fest)
        for fest in selected[1:]:
            self.toplay.append(fest)
        self.flist.append(selected[0])
        self.flleng = len(self.flist)
        self.tpleng = len(self.toplay)
        self.shuffle()

    def recycle(self):
        for card in self.discard:
            self.toplay.append(card)
            self.discard.remove(card)
        
        self.tpleng = len(self.toplay)
        self.shuffle()