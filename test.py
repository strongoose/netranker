import unittest

from netranker import Pairing

class TestPairing(unittest.TestCase):

    def test_init(self):
        pairing = Pairing()

        self.assertTrue(hasattr(pairing, 'uuid'))
        self.assertTrue(hasattr(pairing, 'cards'))

        self.assertEqual(len(pairing.cards), 2)

    def test_uniqueness(self):
        pair1 = Pairing()
        pair2 = Pairing()

        self.assertNotEqual(pair1.uuid, pair2.uuid)
        self.assertNotEqual(pair1.uuid, pair2.uuid)
