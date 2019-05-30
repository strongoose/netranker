import unittest

import jwt

from netranker.core import Pairing
from netranker.storage import InMemoryCardStorage
from netranker.samplers import SimpleRandom

CARD_STORAGE = InMemoryCardStorage()
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
        self.assertEqual(pairing.sampling_method, 'simple random')

        try:
            jwt.decode(pairing.jwt(HMAC_KEY), HMAC_KEY, algorithms=['HS256'])
        except jwt.DecodeError:
            self.fail("Could not decode Pairing JWT")
