import unittest
from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from pymongo import MongoClient

from netranker.app import app
from test_utils import load_test_data, random_card_names, faction_of

DB_NAME = 'netranker-test-%s' % uuid4()
app.config['DATABASE'] = DB_NAME

def setUpModule():
    load_test_data(app.config['CARD_STORAGE'])

def tearDownModule():
    MongoClient().drop_database(DB_NAME)

class TestVoting(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        app.config['RESULT_STORAGE']._results.delete_many({})

    def test_get_new_pairing(self):
        response = self.client.get('/pairing')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers['content-type'], 'application/json')

        cards = response.json.get('cards', None)
        self.assertEqual(len(cards), 2)
        for card in cards:
            self.assertEqual(type(card), str)

        token = response.json.get('token', None)
        try:
            claims = jwt.decode(token, app.config['HMAC_KEY'], algorithms=['HS256'])
        except jwt.DecodeError as exception:
            self.fail('Could not decode pairing jwt: %s' % exception)

        self.assertIn('exp', claims.keys())
        self.assertIn('iat', claims.keys())
        self.assertIn('uuid', claims.keys())
        self.assertIn('cards', claims.keys())

    def test_submit_pairing(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {'winner': response.json.get('cards')[0]}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_submit_pairing_without_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_submit_pairing_without_token(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards', None)

        result = {'winner': cards[0]}

        response = self.client.post('/result', json=result)
        self.assertEqual(response.status_code, 403)

    def test_submit_pairing_with_invalid_token(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards', None)
        invalid_token = jwt.encode(
            {}, 'invalid_secret', algorithm='HS256'
        ).decode('utf-8')

        headers = {'authorization': 'bearer ' + invalid_token}
        result = {'winner': cards[0]}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_invalid_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {'winner': 'An Obviously Made Up Card Name'}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_expired_token(self):
        cards = random_card_names(2)
        expired_jwt = jwt.encode(
            {
                'exp': datetime.utcnow() - timedelta(days=30),
                'cards': cards
            },
            app.config['SIGNING_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

        headers = {'authorization': 'bearer ' + expired_jwt}
        result = {'winner': cards[0]}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_invalid_auth_type(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards')

        headers = {'authorization': 'basic ' + response.json.get('token')}
        result = {'winner': cards[0]}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_multiple_winners(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result_a = {'winner': response.json.get('cards')[0]}
        result_b = {'winner': response.json.get('cards')[1]}

        response_a = self.client.post('/result', json=result_a, headers=headers)
        response_b = self.client.post('/result', json=result_b, headers=headers)
        self.assertEqual(response_a.status_code, 204)
        self.assertEqual(response_b.status_code, 401)

    def test_submit_winner_twice(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result_a = {'winner': response.json.get('cards')[0]}
        result_b = {'winner': response.json.get('cards')[0]}

        response_a = self.client.post('/result', json=result_a, headers=headers)
        response_b = self.client.post('/result', json=result_b, headers=headers)
        self.assertEqual(response_a.status_code, 204)
        self.assertEqual(response_b.status_code, 401)

class TestProduceRanking(unittest.TestCase):

    def setUp(self):
        self.signing_key = 'test signing key'
        app.config['SIGNING_KEY'] = self.signing_key
        self.client = app.test_client()

    def tearDown(self):
        app.config['RESULT_STORAGE']._results.delete_many({})

    def test_empty_ranking(self):
        result = self.client.get('/ranking')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, {'ranking': []})

    def test_single_result_ranking(self):
        response = self.client.get('/pairing')
        headers = {'authorization': 'bearer ' + response.json.get('token')}
        winner = response.json.get('cards')[0]
        response = self.client.post('/result', json={'winner': winner},
                                    headers=headers)

        result = self.client.get('/ranking')
        self.assertEqual(result.status_code, 200)

        winner_faction = app.config['CARD_STORAGE'].lookup(
            {'name': winner}
        )['faction']

        ranking = {
            'ranking': [
                {
                    'card': {
                        'name': winner,
                        'faction': winner_faction
                    },
                    'score': 1
                }
            ]
        }
        self.assertEqual(result.json, ranking)

    def test_multiple_result_ranking(self):
        first, second, third = random_card_names(3)

        results = [
            {
                'winner': first,

                'claims': {
                    'cards': [first, second],
                    'uuid': '1',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': first,
                'claims': {
                    'cards': [first, third],
                    'uuid': '2',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            },
            {
                'winner': second,
                'claims': {
                    'cards': [second, third],
                    'uuid': '3',
                    'iat': datetime.now() - timedelta(minutes=5),
                    'exp': datetime.now() - timedelta(minutes=5) + timedelta(days=30)
                }
            }
        ]

        for result in results:
            headers = {
                'authorization': 'bearer ' + jwt.encode(
                    result['claims'], app.config['HMAC_KEY'], algorithm='HS256'
                ).decode('utf-8')
            }
            self.client.post(
                '/result', json={'winner': result['winner']}, headers=headers
            )

        result = self.client.get('/ranking')
        self.assertEqual(result.status_code, 200)

        expected_ranking = {
            'ranking': [
                {
                    'score': 2,
                    'card': {
                        'name': first,
                        'faction': faction_of(first),
                    }
                },
                {
                    'score': 1,
                    'card': {
                        'name': second,
                        'faction': faction_of(second),
                    }
                },
            ]
        }
        self.assertEqual(result.json, expected_ranking)
