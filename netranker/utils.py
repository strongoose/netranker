import json
from itertools import groupby
import argparse

import requests
from pymongo import MongoClient

def get_title(card):
    return card['title']

def fetch_cards_from_netrunnerdb():
    return requests.get(
        'https://netrunnerdb.com/api/2.0/public/cards'
    ).json()['data']

def load_cards_from_nrdb(database):
    card_data = fetch_cards_from_netrunnerdb()
    load_cards(database, card_data)

def load_cards_from_disk(database):
    with open('downloads/card_data.json', 'r') as card_file:
        card_data = json.load(card_file)
    load_cards(database, card_data)

def load_cards(database, card_data):
    card_data = sorted(card_data, key=get_title)
    database.cards.insert_many([
        {
            'name': name,
            'side': [printing['side_code'] for printing in printings][0],
            'packs': [printing['pack_code'] for printing in printings]
        }
        for name, printings in groupby(card_data, get_title)
    ])

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
        '--database', default='netranker', help='Database name')
    load_cards_parser.add_argument(
        '--host', default='localhost', help='Database host')
    load_cards_parser.add_argument(
        '--port', default=27017, help='Database port')
    args = parser.parse_args()

    database = MongoClient(host=args.host, port=args.port)[args.database]
    if args.local:
        load_cards_from_disk(database)
    else:
        load_cards_from_nrdb(database)
