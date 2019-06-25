import json
from itertools import groupby
import argparse

import requests
from pymongo import MongoClient

from netranker.card_storage import MongoDbCardStorage, InMemoryCardStorage

def get_title(card):
    return card['title']

def fetch_cards_from_netrunnerdb():
    return requests.get(
        'https://netrunnerdb.com/api/2.0/public/cards'
    ).json()['data']

def load_cards_from_nrdb(card_storage):
    card_data = fetch_cards_from_netrunnerdb()
    load_cards(card_storage, card_data)

def load_cards_from_disk(card_storage):
    with open('downloads/card_data.json', 'r') as card_file:
        card_data = json.load(card_file)
    load_cards(card_storage, card_data)

def load_cards(card_storage, card_data):
    card_data = sorted(card_data, key=get_title)
    for name, printings in groupby(card_data, get_title):
        printings = list(printings)
        card_storage.insert(
            {
                'name': name,
                'side': [printing['side_code'] for printing in printings][0],
                'packs': [printing['pack_code'] for printing in printings],
                'faction': [printing['faction_code'] for printing in printings][0]
            }
        )

def main():
    parser = argparse.ArgumentParser(description='Netranker utility scripts')
    subparsers = parser.add_subparsers(
        required=True, help='Sub-command help',
    )
    load_cards_parser = subparsers.add_parser(
        'load_cards', help='Load cards into a database')
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

    if args.card_storage_backend == 'MongoDbCardStorage':
        card_storage = MongoDbCardStorage(args.database, host=args.host, port=args.port)
    elif args.card_storage_backend == 'InMemoryCardStorage':
        card_storage = InMemoryCardStorage()

    if args.local:
        load_cards_from_disk(card_storage)
    else:
        load_cards_from_nrdb(card_storage)
