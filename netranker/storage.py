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

    def find(self):
        return self._results


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

    def find(self):
        return list(self._results.find({}, {'_id': 0}))
