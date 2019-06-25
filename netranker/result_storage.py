from abc import ABC, abstractmethod

from pymongo import MongoClient

class BaseResultStorage(ABC):

    @abstractmethod
    def register(result):
        pass

    @abstractmethod
    def list(self, result):
        pass

class InMemoryResultStorage(BaseResultStorage):

    def __init__(self, *_, **__):
        self._results = []

    def register(self, result):
        self._results.append(result)

    def list(self):
        return self._results

class MongoDbResultStorage():

    def __init__(self, database, **kwargs):
        self._results = MongoClient(**kwargs)[database].results

    def register(self, result):
        return self._results.insert_one(result)

    def list(self):
        return list(self._results.find({}, {'_id': 0}))
