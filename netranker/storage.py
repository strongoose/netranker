class InMemoryDatabase():

    def __init__(self):
        self.cards = InMemoryCollection()

class InMemoryCollection():

    def __init__(self):
        self.__list__ = []

    def insert_one(self, item):
        self.__list__.append(item)

    def insert_many(self, items):
        for item in items:
            self.insert_one(item)

    def find(self):
        return self.__list__
