import unittest

import jwt

from app import app

class TestVoting(unittest.TestCase):

    def setUp(self):
        self.signing_key = 'test signing key'
        app.config['signing_key'] = self.signing_key
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

        self.assertIn('iat', claims.keys())
        self.assertIn('exp', claims.keys())
        self.assertIn('cards', claims.keys())

    def test_submit_pairing(self):
        response = self.client.get('/pairing')

        headers = {'authorization': response.json.get('token')}
        result = {'winner': response.json.get('cards')[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_submit_pairing_without_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': response.json.get('token')}
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
        invalid_token = jwt.encode({}, 'invalid_secret', algorithm='HS256')

        headers = {'authorization': invalid_token}
        result = {'winner': cards[0]}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_submit_pairing_with_invalid_winner(self):
        response = self.client.get('/pairing')

        headers = {'authorization': response.json.get('token')}
        result = {'winner': 'The Shadow: Pulling the Strings'}

        response = self.client.post('/pairing', json=result, headers=headers)
        self.assertEqual(response.status_code, 401)
