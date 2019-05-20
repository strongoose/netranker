import unittest

import jwt

from app import app

class TestVoting(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_get_new_pairing(self):
        response = self.client.get('/pairing')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers['content-type'], 'application/json')

        pairing = response.json.get('pairing', None)
        self.assertEqual(len(pairing), 2)

        token = response.json.get('token', None)
