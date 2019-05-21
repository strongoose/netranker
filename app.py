from flask import Flask, jsonify

from datetime import datetime, timedelta

import jwt

app = Flask(__name__)

@app.route("/pairing", methods=['GET'])
def pairing():
    cards = ['Temujin Contract', 'Şifr']

    issued = datetime.utcnow()
    jwt_claim = {
        'cards': cards,
        'iat': issued,
        'exp': issued + timedelta(hours=12)
    }

    pairing = {
        'cards': cards,
        'token': jwt.encode(jwt_claim, app.config['signing_key'], algorithm='HS256').decode('utf-8') }

    return jsonify(pairing)
