from datetime import datetime, timedelta

import jwt

class Pairing():

    def __init__(self, sampler):

        self.sampling_method = str(sampler)
        self.cards = sampler.sample(2)

    def jwt(self, hmac_key):
        return jwt.encode(
            {
                'cards': self.cards,
                'exp': datetime.utcnow() + timedelta(days=30)
            },
            hmac_key,
            algorithm='HS256'
        ).decode('utf-8')
