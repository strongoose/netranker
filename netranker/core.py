from datetime import datetime, timedelta
from collections import Counter
from abc import ABC, abstractmethod

import jwt

class BasePairing(ABC):

    @abstractmethod
    def issue_jwt(self):
        pass

    @abstractmethod
    def sample(self):
        pass

class RandomPairing(BasePairing):

    def __init__(self, storage):
        self.storage = storage
        self.method = 'simple random'
        self.sample()

    def serialize(self, hmac_key):
        return {
            'cards': self.cards,
            'token': self.issue_jwt(hmac_key)
        }

    def issue_jwt(self, hmac_key):
        claims = {
            'cards': self.cards,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(
            claims, hmac_key, algorithm='HS256'
        ).decode('utf-8')

    def sample(self):
        self.cards = [
            card_details['name']
            for card_details in self.storage.sample(2)
        ]

class Result():

    def __init__(self, winner, pairing, storage):
        if winner not in pairing['cards']:
            raise Exception
        self.winner = winner
        self.pairing = pairing
        self._storage = storage

        self._register()

    def _register(self):
        self._storage.insert_one({
            'winner': self.winner,
            'pairing': self.pairing,
            'created_at': datetime.now()
        })

def generate_ranking(storage):
    all_winners = [result['winner'] for result in storage.find()]
    winners_by_wins = [
        {
            'card': {
                'name': card,
                'faction': storage.lookup({'name': card})['faction']
            },
            'score': score
        }
        for card, score in Counter(all_winners).most_common()
    ]
    return winners_by_wins
