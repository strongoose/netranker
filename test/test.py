import unittest

from netranker.core import Pairing
from netranker.ports import CardSampler
from test.adapters import TestSampler

class TestPairing(unittest.TestCase):

    def setUp(self):
        test_sample = ['54321', '12345']
        self.test_sampler = TestSampler(test_sample)

    def test_init(self):
        '''
        Test that Pairings initialise correctly with a UUID and a pair of cards
        '''
        pairing = Pairing(card_sampler=self.test_sampler)

        self.assertTrue(hasattr(pairing, 'uuid'))
        self.assertTrue(hasattr(pairing, 'cards'))

        self.assertEqual(pairing.cards, ['54321', '12345'])

    def test_uniqueness(self):
        '''
        Test that the UUIDs on two different Pairings are unique
        '''
        pair1 = Pairing(card_sampler=self.test_sampler)
        pair2 = Pairing(card_sampler=self.test_sampler)

        self.assertNotEqual(pair1.uuid, pair2.uuid)
        self.assertNotEqual(pair1.uuid, pair2.uuid)

class TestCardSampler(unittest.TestCase):

    def test_no_init(self):
        '''
        Card sampler is an abstract class and requires __init__ to be
        implemented by child classes
        '''
        with self.assertRaises(TypeError):
            CardSampler()
