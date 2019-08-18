from os import environ

from flask import Flask, request
from flask_restful import Api, Resource
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest

import jwt

from netranker.core import (
    RandomPairing, Result, generate_ranking, InvalidWinner, DuplicateResult
)

def configure(app):
    app.config['CARD_STORAGE'] = app.config['CARD_STORAGE'](
        app.config['DATABASE'], host=app.config['DB_HOST'],
        port=app.config['DB_PORT'])

    app.config['RESULT_STORAGE'] = app.config['RESULT_STORAGE'](
        app.config['DATABASE'], host=app.config['DB_HOST'],
        port=app.config['DB_PORT'])

def extract_bearer_token(request):
    auth_header = request.headers.get('authorization', None)
    if auth_header is None:
        raise Forbidden

    authorization, token = auth_header.split(' ')
    if authorization.lower() != 'bearer':
        raise Unauthorized

    return token

def decode_bearer_token(request):
    token = extract_bearer_token(request)
    try:
        return jwt.decode(
            token, app.config['HMAC_KEY'], algorithms=['HS256']
        )
    except jwt.InvalidTokenError:
        raise Unauthorized

class PairingApi(Resource):

    def get(self):
        pairing = RandomPairing(app.config['CARD_STORAGE'])
        response = pairing.serialize(app.config['HMAC_KEY'])
        return response, 200

class ResultApi(Resource):
    def post(self):
        pairing_claim = decode_bearer_token(request)

        winner = request.json.get('winner', None)
        if winner is None:
            raise BadRequest

        try:
            Result(winner, pairing_claim, storage=app.config['RESULT_STORAGE'])
        except (InvalidWinner, DuplicateResult) as e:
            raise Unauthorized

        return None, 204

class RankingApi(Resource):

    def get(self):
        return {'ranking': generate_ranking(app.config['CARD_STORAGE'], app.config['RESULT_STORAGE'])}, 200

app = Flask(__name__)
app.config.from_object('config.default')
app.config.from_envvar('NETRANKER_CONFIG', silent=True)
configure(app)
api = Api(app)

api.add_resource(PairingApi, '/pairing')
api.add_resource(ResultApi, '/result')
api.add_resource(RankingApi, '/ranking')
