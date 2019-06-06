from secrets import token_hex

from netranker.storage import MongoDbStorage
from netranker.samplers import SimpleRandom

HMAC_KEY = token_hex(256)
RESTFUL_JSON = {'ensure_ascii': False}
STORAGE = MongoDbStorage
SAMPLER = SimpleRandom
DATABASE = 'netranker'
DB_HOST = 'localhost'
DB_PORT = 27017
