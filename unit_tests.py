import unittest
from datetime import datetime, timedelta

import jwt

from netranker.core import Pairing, Result
from netranker.storage import InMemoryCardStorage, InMemoryResultStorage
from netranker.samplers import SimpleRandom

CARD_STORAGE = InMemoryCardStorage()
RESULT_STORAGE = InMemoryResultStorage()
SAMPLER = SimpleRandom(storage=CARD_STORAGE)
HMAC_KEY = 'test signing key'

def setUpModule():
    CARD_STORAGE._cards = [
        {'name': 'Paige Piper', 'packs': ['val']},
        {'name': 'Fall Guy', 'packs': ['dt', 'core2']},
        {'name': 'Seidr Laboratories: Destiny Defined', 'packs': ['td', 'sc19']},
        {'name': 'Leprechaun', 'packs': ['up']},
        {'name': 'Data Loop', 'packs': ['fm']},
        {'name': 'Threat Level Alpha', 'packs': ['cd']},
        {'name': 'Cyberdex Trial', 'packs': ['om']},
        {'name': "An Offer You Can't Refuse", 'packs': ['oh']},
        {'name': 'Musaazi', 'packs': ['ka']},
        {'name': 'Brain-Taping Warehouse', 'packs': ['val']}
    ]

class TestSamplers(unittest.TestCase):

    def test_simple_random_sampler(self):
        sampler = SimpleRandom(CARD_STORAGE)

        samples = [
            sampler.sample(i)
            for i in range(0, 10)
        ]

        for i, sample in enumerate(samples):
            self.assertEqual(type(sample), list)
            self.assertEqual(len(sample), i)
            for card in sample:
                self.assertTrue(type(card), str)

class TestPairing(unittest.TestCase):

    def test_pairing_creation(self):
        pairing = Pairing(SAMPLER)

        self.assertEqual(type(pairing.cards), list)
        for card in pairing.cards:
            self.assertEqual(type(card), str)
        self.assertEqual(pairing.sampling_method, 'simple random')

        try:
            jwt.decode(pairing.issue_jwt(HMAC_KEY), HMAC_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            self.fail("Invalid JWT Token")

class TestResult(unittest.TestCase):

    def test_result_creation(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Hostile Takeover'
        try:
            result = Result(winner, pairing, RESULT_STORAGE)
            result.register()
        except:
            self.fail('Could not create result.')

        stored_results = list(result._storage._results)
        self.assertEqual(len(stored_results), 1)

        result = stored_results[0]

        self.assertIn('winner', result.keys())
        self.assertIn('pairing', result.keys())
        self.assertEqual(result['winner'], winner)
        self.assertEqual(result['pairing'], pairing)

    def test_result_creation_with_invalid_winner(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        },
        winner = 'Account Siphon'
        with self.assertRaises(Exception):
            Result(winner, pairing, RESULT_STORAGE)
