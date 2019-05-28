import random

class SimpleRandom():

    def __init__(self, database):
        self.database = database

    def sample(self, size):
        return random.sample(self.database.cards.find(), size)
