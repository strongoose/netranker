from netranker.samplers import SimpleRandom
from netranker.storage import InMemoryDatabase

class Pairing():

    def __init__(self, database=None, sampler=None):
        if database is None:
            database = InMemoryDatabase()
        if sampler is None:
            sampler = SimpleRandom

        self.sampling_method = str(sampler(database=database))
        self.cards = sampler(database=database).sample(2)
