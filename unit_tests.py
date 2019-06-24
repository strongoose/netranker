import unittest
from datetime import datetime, timedelta

import jwt

from netranker.core import Pairing, Result, generate_ranking
from netranker.storage import InMemoryStorage
from netranker.samplers import SimpleRandom
from netranker.utils import load_cards_from_disk

class TestSamplers(unittest.TestCase):

    def setUp(self):
        self.card_storage = InMemoryStorage()
        load_cards_from_disk(self.card_storage)

    def test_simple_random_sampler(self):
        sampler = SimpleRandom(self.card_storage)

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

    def setUp(self):
        card_storage = InMemoryStorage()
        card_storage._cards = [
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
        self.sampler = SimpleRandom(card_storage)

    def test_pairing_creation(self):
        pairing = Pairing(self.sampler)

        self.assertEqual(type(pairing.cards), list)
        for card in pairing.cards:
            self.assertEqual(type(card), str)
        self.assertEqual(pairing.sampling_method, 'simple random')

        try:
            jwt.decode(pairing.issue_jwt('test key'), 'test key', algorithms=['HS256'])
        except jwt.InvalidTokenError:
            self.fail("Invalid JWT Token")

class TestResult(unittest.TestCase):

    def setUp(self):
        self.result_storage = InMemoryStorage()

    def tearDown(self):
        self.result_storage = InMemoryStorage()

    def test_result_creation(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Hostile Takeover'
        try:
            result = Result(winner, pairing, self.result_storage)
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
        }
        winner = 'Account Siphon'
        with self.assertRaises(Exception):
            Result(winner, pairing, self.result_storage)

class TestRankings(unittest.TestCase):

    def setUp(self):
        self.result_storage = InMemoryStorage()

    def tearDown(self):
        self.result_storage = InMemoryStorage()

    def test_empty_ranking(self):
        ranking = generate_ranking(self.result_storage)
        self.assertEqual(ranking, [])

    def test_single_item_ranking(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Hostile Takeover'
        Result(winner, pairing, self.result_storage)
        ranking = generate_ranking(self.result_storage)

        self.assertEqual(ranking, ['Hostile Takeover'])

    def test_several_item_ranking(self):
        results = [
            {
                'winner': 'Astroscript Pilot Program',
                'claims': {
                    'cards': ['Astroscript Pilot Program', 'Philotic Entanglement'],
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': 'Astroscript Pilot Program',
                'claims': {
                    'cards': ['Astroscript Pilot Program', 'Philotic Entanglement'],
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': 'Philotic Entanglement',
                'claims': {
                    'cards': ['Philotic Entanglement', 'Toshiyuki Sakai'],
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            }
        ]
        for result in results:
            Result(result['winner'], result['claims'], self.result_storage)
        ranking = generate_ranking(self.result_storage)

        self.assertEqual(ranking, ['Astroscript Pilot Program', 'Philotic Entanglement'])
