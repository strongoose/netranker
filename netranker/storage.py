from abc import ABC, abstractmethod
from random import sample

from pymongo import MongoClient

class BaseCardStorage(ABC):

    @abstractmethod
    def sample(self):
        pass

class InMemoryCardStorage():

    def __init__(self):
        self._cards = []

    def sample(self, k):
        return sample(self._cards, k)

class MongoDbCardStorage():

    def __init__(self, database, **kwargs):
        self._collection = MongoClient(**kwargs)[database].cards

    def sample(self, k):
        return list(self._collection.aggregate([
            {'$sample': {'size': k}},
            {'$project': {'_id': 0}}
        ]))

class BaseResultStorage(ABC):

    @abstractmethod
    def register(self, result):
        pass

class InMemoryResultStorage():

    def __init__(self):
        self._results = []

    def insert(self, result):
        self._results.append(result)

class MongoDbResultStorage():

    def __init__(self, database, **kwargs):
        self._collection = MongoClient(**kwargs)[database].cards

    def insert(self, result):
        self._collection.insert(result)
