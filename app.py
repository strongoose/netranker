from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/pairing", methods=['GET'])
def pairing():
    response_json = {
        'pairing': ['Temujin Contract', 'Şifr'],
        'token': 'foo'
    }

    return jsonify(response_json)
