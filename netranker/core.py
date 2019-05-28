from netranker.samplers import SimpleRandom

class Pairing():

    def __init__(self, sampler=SimpleRandom):
        self.cards = sampler.sample(2)
