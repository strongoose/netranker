import random

class SimpleRandom():

    def __str__(self):
        return "simple random"

    def __init__(self, database):
        self.database = database

    def sample(self, size):
        return random.sample(self.database.cards.find(), size)
