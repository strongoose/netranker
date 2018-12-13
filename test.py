import unittest

from netranker import Pairing

class TestPairing(unittest.TestCase):

    def test_init(self):
        pair = Pairing()

        self.assertTrue(hasattr(pair, 'uuid'))
        self.assertTrue(hasattr(pair, 'cards'))

        self.assertEqual(len(pair.cards), 2)

    def test_uniqueness(self):
        pair1 = Pairing()
        pair2 = Pairing()

        self.assertNotEqual(pair1.uuid, pair2.uuid)
        self.assertNotEqual(pair1.uuid, pair2.uuid)
