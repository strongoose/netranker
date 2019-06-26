from abc import ABC, abstractmethod
from functools import reduce

from pymongo import MongoClient

class BaseResultStorage(ABC):

    @abstractmethod
    def register(result):
        pass

    @abstractmethod
    def list(self, result):
        pass

    @abstractmethod
    def lookup(self, filter):
        pass

class InMemoryResultStorage(BaseResultStorage):

    def __init__(self, *_, **__):
        self._results = []

    def register(self, result):
        self._results.append(result)

    def list(self):
        return self._results

    def lookup(self, filter):

        def matches(result, filter):
            for path, value in filter.items():
                keys = path.split('.')
                if reduce(dict.get, keys, result) != value:
                    return False
            return True

        result = [
            result for result in self._results
            if matches(result, filter)
        ]

        if result == []:
            return None
        return result[0]

class MongoDbResultStorage():

    def __init__(self, database, **kwargs):
        self._results = MongoClient(**kwargs)[database].results

    def register(self, result):
        return self._results.insert_one(result)

    def list(self):
        return list(self._results.find({}, {'_id': 0}))

    def lookup(self, filter):
        return self._results.find_one(filter)
