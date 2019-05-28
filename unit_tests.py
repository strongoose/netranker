import unittest

from netranker.core import Pairing
from netranker.storage import InMemoryDatabase
from netranker.samplers import SimpleRandom
from netranker.utils import load_cards

database = InMemoryDatabase()
sampler = SimpleRandom(database=database)

def setUpModule():
    load_cards(database.cards)

class TestPairing(unittest.TestCase):

    def test_pairing_creation(self):
        pairing = Pairing(sampler=SimpleRandom)
