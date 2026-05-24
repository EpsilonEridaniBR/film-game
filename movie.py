



class MOVIE:
    def __init__(self, script, director, actor):
        self.script = script
        self.director = director
        self.actor = actor
        self.name = str(self.script) + "+" + str(self.director) +  "+" + str(self.actor)
        self.value = 0

    def __str__(self):
        return self.name
    
    def roll(self):
        v = self.script.roll() + self.director.roll() + self.actor.roll()
        self.value = self.value + v

    def modify(self, string):
        if string in self.modifiers:
            self.value = self.value + int(self.modifiers[string][1:])

    def applyMods(self):
        self.modifiers = {}
        self.modifiers.update(self.script.modifiers)
        self.modify(self.director.name)
        self.modifiers.update(self.director.modifiers)
        self.modify(self.actor.name)
        self.modifiers.update(self.actor.modifiers)