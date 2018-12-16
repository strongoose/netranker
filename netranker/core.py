from uuid import uuid4 as uuid

class Pairing():

    def __init__(self, card_sampler):
        self.uuid = uuid()
        self.cards = card_sampler.sample()
