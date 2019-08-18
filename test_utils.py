from random import sample

from test_data import CARDS

def load_test_data(card_storage):
    for card in CARDS:
        card_storage.insert(card)

def random_card_names(size):
    return [card['name'] for card in sample(CARDS, size)]

def faction_of(card_name):
    for card in CARDS:
        if card['name'] == card_name:
            return card['faction']
    return None
