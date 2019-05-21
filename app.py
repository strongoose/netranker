from datetime import datetime, timedelta
from secrets import token_hex

from flask import Flask, request
from flask_restful import Api, Resource

import jwt

app = Flask(__name__)
app.config['SIGNING_KEY'] = token_hex(256)
# Turns off ASCII escaping for JSON data
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
api = Api(app)

class Pairing(Resource):
    def get(self):
        cards = ['Temüjin Contract', 'Şifr']
        issued = datetime.utcnow()
        jwt_claim = {'cards': cards,
                     'iat': issued,
                     'exp': issued + timedelta(hours=12)}
        token = jwt.encode(jwt_claim, app.config['SIGNING_KEY'], algorithm='HS256')
        pairing = {
            'cards': cards,
            'token': token.decode('utf-8')
        }

        return pairing, 200

    def post(self):
        auth_token = request.headers.get('authorization', None)
        if auth_token is None:
            return 'Forbidden', 403
        try:
            claims = jwt.decode(
                auth_token, app.config['SIGNING_KEY'], algorithms=['HS256']
            )
        except jwt.InvalidSignatureError:
            return 'Unauthorized', 401
        winner = request.json.get('winner', None)
        if winner is None:
            return 'Bad Request', 400
        if winner not in claims['cards']:
            return 'Unauthorized', 401
        return None, 204

api.add_resource(Pairing, '/pairing')
