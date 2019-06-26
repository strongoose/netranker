import unittest
from datetime import datetime, timedelta

import jwt

from netranker.core import (
    RandomPairing, Result, generate_ranking, DuplicateResult, InvalidWinner
)
from netranker.card_storage import InMemoryCardStorage
from netranker.result_storage import InMemoryResultStorage
from netranker.utils import load_cards_from_disk

class TestRandomPairing(unittest.TestCase):

    def setUp(self):
        card_storage = InMemoryCardStorage()
        load_cards_from_disk(card_storage)
        self.pairing = RandomPairing(card_storage)

    def test_pairing_creation(self):
        self.assertEqual(type(self.pairing.cards), list)
        for card in self.pairing.cards:
            self.assertEqual(type(card), str)
        self.assertEqual(self.pairing.method, 'simple random')

    def test_issue_jwt(self):
        try:
            jwt.decode(self.pairing.issue_jwt('test key'), 'test key', algorithms=['HS256'])
        except jwt.InvalidTokenError:
            self.fail("Invalid JWT Token")

    def test_serialize(self):
        json = self.pairing.serialize('test key')
        self.assertIn('cards', json)
        self.assertIn('token', json)
        self.assertEqual(type(json['cards']), list)
        self.assertEqual(type(json['token']), str)

    def test_sample(self):
        old_cards = self.pairing.cards
        self.pairing.sample()
        self.assertNotEqual(old_cards, self.pairing.cards)

class TestResult(unittest.TestCase):

    def setUp(self):
        self.result_storage = InMemoryResultStorage()

    def test_result_creation(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'uuid': '1234',
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
            'uuid': '1234',
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Account Siphon'
        with self.assertRaises(InvalidWinner):
            Result(winner, pairing, self.result_storage)

    def test_duplicate_result_creation(self):
        pairing = {
            'cards': ['Account Siphon', 'Contract Killer'],
            'uuid': '1234',
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Account Siphon'
        Result(winner, pairing, self.result_storage)

        with self.assertRaises(DuplicateResult):
            Result('Contract Killer', pairing, self.result_storage)

class TestRankings(unittest.TestCase):

    def setUp(self):
        self.card_storage = InMemoryCardStorage()
        load_cards_from_disk(self.card_storage)
        self.result_storage = InMemoryResultStorage()

    def test_empty_ranking(self):
        ranking = generate_ranking(self.card_storage, self.result_storage)
        self.assertEqual(ranking, [])

    def test_single_item_ranking(self):
        pairing = {
            'cards': ['Hostile Takeover', 'Contract Killer'],
            'uuid': '1',
            'iat': datetime.now() - timedelta(minutes=5),
            'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
        }
        winner = 'Hostile Takeover'
        Result(winner, pairing, self.result_storage)
        ranking = generate_ranking(self.card_storage, self.result_storage)

        expected_ranking = [
            {
                'card': {
                    'name': 'Hostile Takeover',
                    'faction': 'weyland-consortium',
                },
                'score': 1
            }
        ]
        self.assertEqual(ranking, expected_ranking)

    def test_several_item_ranking(self):
        results = [
            {
                'winner': 'AstroScript Pilot Program',
                'claims': {
                    'cards': ['AstroScript Pilot Program', 'Philotic Entanglement'],
                    'uuid': '1',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': 'AstroScript Pilot Program',
                'claims': {
                    'cards': ['AstroScript Pilot Program', 'Philotic Entanglement'],
                    'uuid': '2',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': 'Philotic Entanglement',
                'claims': {
                    'cards': ['Philotic Entanglement', 'Toshiyuki Sakai'],
                    'uuid': '3',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            }
        ]
        for result in results:
            Result(result['winner'], result['claims'], self.result_storage)
        ranking = generate_ranking(self.card_storage, self.result_storage)

        expected_ranking = [
            {
                'card': {
                    'name': 'AstroScript Pilot Program',
                    'faction': 'nbn',
                },
                'score': 2
            },
            {
                'card': {
                    'name': 'Philotic Entanglement',
                    'faction': 'jinteki',
                },
                'score': 1
            }
        ]

        self.assertEqual(ranking, expected_ranking)

class TestInMemoryResultStorage(unittest.TestCase):

    def test_lookup(self):
        result_storage = InMemoryResultStorage()

        result_storage.register({
            'winner': 'Architect',
            'pairing': {
                'cards': ['Architect', 'Underway Grid'],
                'uuid': '1234567890',
            }
        })

        self.assertIsNotNone(result_storage.lookup({'pairing.uuid': '1234567890'}))
        self.assertIsNone(result_storage.lookup({'pairing.uuid': 'notthere'}))
