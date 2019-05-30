import random

class SimpleRandom():

    def __str__(self):
        return "simple random"

    def __init__(self, storage):
        self.storage = storage

    def sample(self, size):
        return self.storage.sample(size)
