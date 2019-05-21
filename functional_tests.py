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
            jwt.decode(token, self.signing_key, algorithms=['HS256'])
        except jwt.DecodeError as exception:
            self.fail('Could not decode pairing jwt: %s' % exception)
