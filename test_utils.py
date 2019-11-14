from random import sample

from test_data import CARDS

def load_test_data(card_storage):
    for card in CARDS:
        # pymongo adds '_id' fields to documents it inserts; to prevent this
        # mutating the top level CARDS list we make a copy each doc before
        # inserting
        card_storage.insert(card.copy())

def random_cards(size):
    return sample(CARDS, size)
