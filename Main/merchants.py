"""
Contains a central database of all merchants available in the simulation.
"""

MERCHANTS = {
    'coffee': {
        'ids': ['MERCH_STARBUCKS_01', 'MERCH_COSTA_02', 'MERCH_PRET_03'],
        'channel': 'POS',
        'country': 'GB'
    },
    'lunch': {
        'ids': ['MERCH_PRET_03', 'MERCH_GREGGS_01', 'MERCH_SUBWAY_02', 'MERCH_EAT_05'],
        'channel': 'POS',
        'country': 'GB'
    },
    'groceries': {
        'ids': ['MERCH_TESCO_01', 'MERCH_SAINSBURYS_02', 'MERCH_ALDI_03', 'MERCH_M&S_04'],
        'channel': 'POS',
        'country': 'GB'
    },
    'utility_bill': {
        'ids': ['MERCH_THAMES_WATER_01', 'MERCH_OCTOPUS_02'],
        'channel': 'Online',
        'country': 'GB'
    },
    'online_shopping': {
        'ids': ['MERCH_AMAZON_UK', 'MERCH_SHEIN_UK'],
        'channel': 'Online',
        'country': 'GB'
    },
    'food_delivery': {
        'ids': ['MERCH_DELIVEROO', 'MERCH_UBER_EATS'],
        'channel': 'Online',
        'country': 'GB'
    }
}