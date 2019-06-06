from secrets import token_hex

from netranker.storage import InMemoryStorage
from netranker.samplers import SimpleRandom

HMAC_KEY = token_hex(256)
RESTFUL_JSON = {'ensure_ascii': False}
CARD_STORAGE = InMemoryStorage()
RESULT_STORAGE = InMemoryStorage()
SAMPLER = SimpleRandom(CARD_STORAGE)
