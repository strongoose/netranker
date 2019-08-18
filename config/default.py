from secrets import token_hex

from netranker.result_storage import MongoDbResultStorage
from netranker.card_storage import MongoDbCardStorage

HMAC_KEY = token_hex(256)
RESTFUL_JSON = {'ensure_ascii': False}
CARD_STORAGE = MongoDbCardStorage
RESULT_STORAGE = MongoDbResultStorage
DATABASE = 'netranker'
DB_HOST = 'localhost'
DB_PORT = 27017
