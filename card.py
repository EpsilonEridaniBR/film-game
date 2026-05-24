import random

class CARD:
    def __init__(self, no, category, name, quantity):
        self.no = no
        self.cat = category
        self.name = name
        self.qty = quantity
        self.modifiers = {}

    def __str__(self):
        return self.name + " (" + self.cat + ")"
    
    def assignVal(self, val):
        self.dice = int(val[2])
        self.qtyDice = int(val[0])
    
    def calcProb(self, decksize):
        self.avg = (self.dice+1)*self.qtyDice/2
        self.expectance = round(self.avg*self.qty/decksize, 4)

    def roll(self):
        rsum = 0;
        for i in range(self.qtyDice):
            rsum = rsum + random.randint(1, self.dice)

        return rsum

    def attachModifier(self, name, mod):
        self.modifiers[name] = mod

    def info(self):
        print(self.name + " - " + self.cat)
        if hasattr(self, "avg"):
            print("AVG: " + str(self.avg) + "+mod; EXP: " + str(self.expectance))
        print(self.modifiers)
        