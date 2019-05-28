from netranker.samplers import SimpleRandom

class Pairing():

    def __init__(self, sampler):

        self.sampling_method = str(sampler)
        self.cards = sampler.sample(2)
