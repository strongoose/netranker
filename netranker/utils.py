import requests
from itertools import groupby

def get_title(card):
    return card['title']

def load_cards(collection):
    card_data = requests.get(
        'https://netrunnerdb.com/api/2.0/public/cards'
    ).json()['data']
    card_data = sorted(card_data, key=get_title)
    collection.insert_many([
        {
            'name': name,
            'packs': [printing['pack_code'] for printing in printings]
        }
        for name, printings in groupby(card_data, get_title)
    ])
