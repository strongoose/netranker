import unittest

import requests

class TestVoting(unittest.TestCase):

    def test_get_new_pairing(self):
        response = requests.get('http://localhost:5000/pairing')

        self.assertEqual(response.status_code, 200)
