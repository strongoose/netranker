#!/usr/bin/env python3

import random
import sys

import requests

NRDB_API = 'https://netrunnerdb.com/api/2.0/public/cards'

def unique_titled(card_data):
    '''
    Return unique cards with newer cards (i.e. core 2.0) taking precedence
    '''
    name_dict = {card['title']: card for card in card_data}
    return name_dict.values()

def with_draft_removed(card_data):
    '''
    Remove draft cards
    '''
    return list(filter(lambda card: card['pack_code'] != 'draft', card_data))

def with_community_cards_removed(card_data):
    '''
    Remove Watch the World Burn and Hired Help
    '''
    return list(filter(
        lambda card: card['title'] not in ['Watch the World Burn', 'Hired Help'],
        card_data))


if __name__ == '__main__':

    card_data = requests.get(NRDB_API).json().get('data')

    if card_data is None:
        print('Could not retreive card data')
        sys.exit(1)

    # print(len(card_data))
    card_data = unique_titled(card_data)
    # print(len(card_data))
    card_data = with_draft_removed(card_data)
    # print(len(card_data))
    card_data = with_community_cards_removed(card_data)
    # print(len(card_data))
    for card in random.sample({card['title'] for card in card_data}, 2):
        print(card)
