import unittest

from netranker.core import Pairing
from netranker.storage import InMemoryDatabase
from netranker.samplers import SimpleRandom

DATABASE = InMemoryDatabase()
SAMPLER = SimpleRandom(database=DATABASE)

def setUpModule():
    DATABASE.cards.insert_many([
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
    ])

class TestSamplers(unittest.TestCase):

    def test_simple_random_sampler(self):
        sampler = SimpleRandom(database=DATABASE)

        samples = [
            sampler.sample(i)
            for i in range(0, 10)
        ]

        for i, sample in enumerate(samples):
            self.assertTrue(type(sample) == list)
            self.assertTrue(len(sample) == i)
            for card in sample:
                self.assertTrue(type(card), str)

class TestPairing(unittest.TestCase):

    def test_pairing_creation(self):
        pairing = Pairing(sampler=SimpleRandom, database=DATABASE)

        self.assertEqual(type(pairing.cards), list)
        self.assertEqual(pairing.sampling_method, 'simple random')
