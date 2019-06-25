from abc import ABC, abstractmethod
from random import sample

from pymongo import MongoClient

class BaseCardStorage(ABC):

    @abstractmethod
    def sample(self, k):
        pass

    @abstractmethod
    def insert(self, card):
        pass

    @abstractmethod
    def lookup(self, filter):
        pass

class InMemoryCardStorage(BaseCardStorage):

    def __init__(self, *_, **__):
        self._cards = []

    def sample(self, k):
        return sample(self._cards, k)

    def insert(self, card):
        self._cards.append(card)

    def lookup(self, filter):

        def matches(card, filter):
            for key, value in filter.items():
                if card[key] != value:
                    return False
            return True

        result = [
            card for card in self._cards
            if matches(card, filter)
        ]

        if result == []:
            return None
        return result[0]

class MongoDbCardStorage(BaseCardStorage):

    def __init__(self, database, **kwargs):
        self._cards = MongoClient(**kwargs)[database].cards

    def sample(self, k):
        return list(self._cards.aggregate([
            {'$sample': {'size': k}},
            {'$project': {'_id': 0}}
        ]))

    def insert(self, card):
        return self._cards.insert_one(card)

    def lookup(self, filter):
        return self._cards.find_one(filter)
