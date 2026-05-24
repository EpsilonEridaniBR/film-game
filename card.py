import random

class Card:
    def __init__(self, no: int, category: str, name: str, quantity: int):
        self.no = no
        self.cat = category
        self.name = name
        self.qty = quantity
        self.modifiers: dict[str, str] = {}

    def __str__(self):
        return self.name + " (" + self.cat + ")"

    def attachModifier(self, name: str, mod):
        self.modifiers[name] = mod

    def info(self):
        print(self.name + " - " + self.cat)
        print(self.modifiers)


class BiddableCard(Card):
    def assignVal(self, val):
        self.qtyDice = int(val[0])
        self.dice = int(val[2])

    def calcProb(self, decksize):
        self.avg = (self.dice + 1) * self.qtyDice / 2
        self.expectance = round(self.avg * self.qty / decksize, 4)

    def roll(self):
        return sum(random.randint(1, self.dice) for _ in range(self.qtyDice))

    def info(self):
        print(self.name + " - " + self.cat)
        print("AVG: " + str(self.avg) + "+mod; EXP: " + str(self.expectance))
        print(self.modifiers)
