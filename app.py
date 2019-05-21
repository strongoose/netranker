from datetime import datetime, timedelta

from flask import Flask
from flask_restful import Api, Resource

import jwt

app = Flask(__name__)
api = Api(app)

class Pairing(Resource):
    def get(self):
        cards = ['Temüjin Contract', 'Şifr']

        issued = datetime.utcnow()
        jwt_claim = {
            'cards': cards,
            'iat': issued,
            'exp': issued + timedelta(hours=12)
        }

        pairing = {
            'cards': cards,
            'token': jwt.encode(jwt_claim, app.config['signing_key'], algorithm='HS256').decode('utf-8')
        }

        return pairing

api.add_resource(Pairing, '/pairing')
