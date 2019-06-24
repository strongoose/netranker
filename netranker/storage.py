from abc import ABC, abstractmethod
from random import sample

from pymongo import MongoClient

class BaseStorage(ABC):

    @abstractmethod
    def sample(self):
        pass

    @abstractmethod
    def insert_one(self, result):
        pass

    @abstractmethod
    def find(self):
        pass

class InMemoryStorage():

    def __init__(self, *_, **__):
        '''
        This accepts args and kwargs so that database configuration can be
        harmlessly passed in even if we're not using a database.
        '''
        self._cards = []
        self._results = []

    def sample(self, k):
        return sample(self._cards, k)

    def insert_one(self, result):
        self._results.append(result)

    def insert_card(self, card):
        self._cards.append(card)

    def find(self):
        return self._results

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

class MongoDbStorage():

    def __init__(self, database, **kwargs):
        self._cards = MongoClient(**kwargs)[database].cards
        self._results = MongoClient(**kwargs)[database].results

    def sample(self, k):
        return list(self._cards.aggregate([
            {'$sample': {'size': k}},
            {'$project': {'_id': 0}}
        ]))

    def insert_one(self, result):
        return self._results.insert_one(result)

    def insert_card(self, card):
        return self._cards.insert_one(card)

    def find(self):
        return list(self._results.find({}, {'_id': 0}))

    def lookup(self, filter):
        return self._cards.find_one(filter)
