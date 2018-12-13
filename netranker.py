from uuid import uuid4 as uuid

class Pairing():
    def __init__(self):
        self.uuid = uuid()
        self.cards = [0,0]
