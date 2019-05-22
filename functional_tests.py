import unittest
from datetime import datetime, timedelta

import jwt

from netranker.app import app

class TestVoting(unittest.TestCase):

    def setUp(self):
        self.signing_key = 'test signing key'
        app.config['SIGNING_KEY'] = self.signing_key
        self.client = app.test_client()

    def test_get_new_pairing(self):
        response = self.client.get('/pairing')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers['content-type'], 'application/json')

        cards = response.json.get('cards', None)
        self.assertEqual(len(cards), 2)

        token = response.json.get('token', None)
        try:
            claims = jwt.decode(token, self.signing_key, algorithms=['HS256'])
        except jwt.DecodeError as exception:
            self.fail('Could not decode pairing jwt: %s' % exception)

        self.assertIn('exp', claims.keys())
        self.assertIn('cards', claims.keys())

    def test_submit_pairing(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {'winner': response.json.get('cards')[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_submit_pairing_without_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_submit_pairing_without_token(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards', None)

        result = {'winner': cards[0]}

        response = self.client.post('/pairing', json=result)
        self.assertEqual(response.status_code, 403)

    def test_submit_pairing_with_invalid_token(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards', None)
        invalid_token = jwt.encode(
            {}, 'invalid_secret', algorithm='HS256'
        ).decode('utf-8')

        headers = {'authorization': 'bearer ' + invalid_token}
        result = {'winner': cards[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_invalid_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': 'bearer ' + response.json.get('token')}
        result = {'winner': 'The Shadow: Pulling the Strings'}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_expired_token(self):
        cards = ['Oversight AI', 'Melange Mining Corp.']
        expired_jwt = jwt.encode(
            {
                'exp': datetime.utcnow() - timedelta(days=30),
                'cards': cards
            },
            self.signing_key,
            algorithm='HS256'
        ).decode('utf-8')

        headers = {'authorization': 'bearer ' + expired_jwt}
        result = {'winner': cards[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_invalid_auth_type(self):
        response = self.client.get('/pairing')
        cards = response.json.get('cards')

        headers = {'authorization': 'basic ' + response.json.get('token')}
        result = {'winner': cards[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)
