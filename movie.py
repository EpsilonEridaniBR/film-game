



class Movie:
    def __init__(self, script, director, actor):
        self.script = script
        self.director = director
        self.actor = actor
        self.name = str(self.script) + "+" + str(self.director) +  "+" + str(self.actor)
        self.value = 0

    def __str__(self):
        return self.name
    
    def roll(self):
        rolls = {
            self.script.name:   self.script.roll(),
            self.director.name: self.director.roll(),
            self.actor.name:    self.actor.roll(),
        }
        self.rolls = rolls
        self.value = self.value + sum(rolls.values())

    def modify(self, string):
        if string in self.modifiers:
            mod = self.modifiers[string]
            self.value = self.value + int(mod)
            self.applied_mods.append((string, mod))

    def applyMods(self):
        self.modifiers = {}
        self.applied_mods = []
        self.modifiers.update(self.script.modifiers)
        self.modify(self.director.name)
        self.modifiers.update(self.director.modifiers)
        self.modify(self.actor.name)
        self.modifiers.update(self.actor.modifiers)