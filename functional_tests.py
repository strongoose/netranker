import unittest

import jwt
import requests

class TestVoting(unittest.TestCase):

    def test_get_new_pairing(self):
        response = requests.get('http://localhost:5000/pairing')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers['content-type'], 'application/json')

        pairing = response.json().get('pairing', None)
        self.assertEqual(len(pairing), 2)

        token = response.json().get('token', None)
