from flask import Flask, jsonify

from datetime import datetime, timedelta

import jwt

app = Flask(__name__)

@app.route("/pairing", methods=['GET'])
def pairing():
    pairing = ['Temujin Contract', 'Şifr']

    issued = datetime.utcnow()
    jwt_claim = {
        'pair': pairing,
        'iat': issued,
        'exp': issued + timedelta(hours=12)
    }

    response_json = {
        'pairing': pairing,
        'token': jwt.encode(jwt_claim, app.config['signing_key'], algorithm='HS256').decode('utf-8') }

    return jsonify(response_json)
