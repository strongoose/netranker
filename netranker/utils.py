import json
from itertools import groupby
import argparse

import requests

from netranker.card_storage import MongoDbCardStorage, InMemoryCardStorage

def fetch_cards_from_netrunnerdb():
    return requests.get(
        'https://netrunnerdb.com/api/2.0/public/cards'
    ).json()['data']

def load_card_data_from_nrdb(card_storage):
    card_data = fetch_cards_from_netrunnerdb()
    load_cards(card_storage, card_data)

def load_card_data_from_disk(card_storage):
    with open('downloads/card_data.json', 'r') as card_file:
        card_data = json.load(card_file)
    load_cards(card_storage, card_data)

def cards_from(card_data):
    '''
    From JSON card data, return an iterator over cards as they should be
    written to our storage backend.
    '''
    get_title = lambda card: card['title']
    card_data = sorted(card_data, key=get_title)
    for _, printings in groupby(card_data, get_title):
        first_printing = list(printings)[0]
        yield first_printing

def load_cards(card_storage, card_data):
    for record in cards_from(card_data):
        card_storage.insert(record)

def main():
    parser = argparse.ArgumentParser(description='Netranker utility scripts')
    subparsers = parser.add_subparsers(
        required=True, help='Sub-command help',
    )
    load_cards_parser = subparsers.add_parser(
        'load-cards', help='Load cards into a database')
    load_cards_parser.add_argument(
        '--local', action='store_true', help='Load cards from local file')
    load_cards_parser.add_argument(
        '--storage_backend', default='MongoDbCardStorage', help='Card storage backend to use')
    load_cards_parser.add_argument(
        '--database', default='netranker', help='Database name')
    load_cards_parser.add_argument(
        '--host', default='localhost', help='Database host')
    load_cards_parser.add_argument(
        '--port', default=27017, help='Database port')
    args = parser.parse_args()

    if args.storage_backend == 'MongoDbCardStorage':
        card_storage = MongoDbCardStorage(args.database, host=args.host, port=args.port)
    elif args.storage_backend == 'InMemoryCardStorage':
        card_storage = InMemoryCardStorage()

    if args.local:
        load_card_data_from_disk(card_storage)
    else:
        load_card_data_from_nrdb(card_storage)
