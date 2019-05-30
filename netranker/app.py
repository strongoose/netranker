from datetime import datetime, timedelta
from secrets import token_hex

from flask import Flask, request
from flask_restful import Api, Resource

import jwt

from netranker.core import Pairing

app = Flask(__name__)
app.config.from_object('netranker.settings')
app.config.from_envvar('NETRANKER_CONFIG', silent=True)
api = Api(app)

class PairingApi(Resource):

    def get(self):
        pairing = Pairing(app.config['SAMPLER'])
        pairing.jwt(app.config['HMAC_KEY'])
        response = {
            'cards': pairing.cards,
            'token': pairing.jwt(app.config['HMAC_KEY'])
        }
        return response, 200

class ResultApi(Resource):
    def post(self):
        auth_header = request.headers.get('authorization', None)
        if auth_header is None:
            return 'Forbidden', 403

        authorization, token = auth_header.split(' ')
        if authorization.lower() != 'bearer':
            return 'Unauthorized', 401

        try:
            claims = jwt.decode(
                token, app.config['HMAC_KEY'], algorithms=['HS256']
            )
        except jwt.InvalidTokenError:
            return 'Unauthorized', 401

        winner = request.json.get('winner', None)
        if winner is None:
            return 'Bad Request', 400
        if winner not in claims['cards']:
            return 'Unauthorized', 401

        return None, 204

class RankingApi(Resource):

    def get(self):
        return {}, 200

api.add_resource(PairingApi, '/pairing')
api.add_resource(ResultApi, '/result')
api.add_resource(RankingApi, '/ranking')
