import unittest
from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from pymongo import MongoClient

from netranker.app import app
import netranker.utils as utils
from netranker.samplers import SimpleRandom
from netranker.storage import MongoDbCardStorage, MongoDbResultStorage

DB_NAME = 'netranker-test-%s' % uuid4()

def setUpModule():
    app.config['CARD_STORAGE'] = MongoDbCardStorage(DB_NAME)
    app.config['RESULT_STORAGE'] = MongoDbResultStorage(DB_NAME)
    utils.load_cards_from_disk(app.config['CARD_STORAGE']._collection)

    app.config['HMAC_KEY'] = 'test hmac key'
    app.config['SAMPLER'] = SimpleRandom(app.config['CARD_STORAGE'])

def tearDownModule():
    MongoClient().drop_database(DB_NAME)

class TestVoting(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

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
        result = {'winner': 'The Shadow: Pulling the Strings'}

        response = self.client.post('/result', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_expired_token(self):
        cards = ['Oversight AI', 'Melange Mining Corp.']
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

class TestProduceRanking(unittest.TestCase):

    def setUp(self):
        self.signing_key = 'test signing key'
        app.config['SIGNING_KEY'] = self.signing_key
        self.client = app.test_client()

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
        self.assertEqual(result.json, {'ranking': [winner]})
