import random

class Peep:
    def __init__(self):
        self.recovery_rate = random.randrange(7,10) # How many seconds it stays in a mood
        self.hunger = random.randrange(50,100) # Drains over time, can replenish with food
        self.social = random.randrange(50,100) # Gets affected by nearby peeps hapiness
        self.religion = random.randrange(50,100) # Increases by seeing miricles and visitng the church. affects chance of going to church
        self.wealth = random.randrange(50,100) # Increased by stealing, being poor makes you more likely to steal
        self.prefrences = [random.randrange(0,32), random.randrange(0,32), random.randrange(0,32)]
        self.prefrences.append(1- self.prefrences[0] - self.prefrences[1]- self.prefrences[2]) 
        # Prefence How much they prefer each attribute. makes them gain it faster and increases its hapiness gain

    def calculate_mood(self):
        self.mood = (self.hunger*self.prefrences[0]) + (self.social*self.prefrences[1]) +(self.religion*self.prefrences[2])+(self.wealth*self.prefrences[3])




