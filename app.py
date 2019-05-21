from datetime import datetime, timedelta

from flask import Flask, request
from flask_restful import Api, Resource

import jwt

app = Flask(__name__)
api = Api(app)

class Pairing(Resource):
    def get(self):
        cards = ['Temüjin Contract', 'Şifr']
        issued = datetime.utcnow()
        jwt_claim = {'cards': cards,
                     'iat': issued,
                     'exp': issued + timedelta(hours=12)}
        token = jwt.encode(jwt_claim, app.config['signing_key'], algorithm='HS256')
        pairing = {
            'cards': cards,
            'token': token.decode('utf-8')
        }

        return pairing

    def post(self):
        auth_token = request.headers.get('authorization', None)
        if auth_token is None:
            return 'Forbidden', 403
        return None, 204

api.add_resource(Pairing, '/pairing')
