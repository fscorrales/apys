#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Source: 
    -   https://github.com/crapher/pyhomebroker
    -   https://github.com/juanmarti81/EPGB_HomeBroker
Purpose: Get constant data from HomeBroker
Require package: 
    -   pip install pyhomebroker
    -   pip install pyhomebroker --upgrade --no-cache-dir
"""

import argparse
import inspect
import json
import os
import sys
import time
from dataclasses import dataclass, field

import pandas as pd
from pyhomebroker import HomeBroker

from ..utils.pydyverse import PrintTibble
from .homebroker_login import HomeBrokerLogin


# --------------------------------------------------
@dataclass
class LivePrice(HomeBrokerLogin):
    """
    Get constant datafrom HomeBroker
    :param hb must be initialized first
    """
    securities: pd.DataFrame = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        self.login()
        self.init_securities(['GGAL - 48hs', 'GGAL - 24hs', 'GGAL - spot'])
        self.get_data()

    # --------------------------------------------------
    def init_securities(self, symbols:list) -> pd.DataFrame:
        df = pd.DataFrame(
            {'symbol' : symbols},
            columns=[
                "symbol", "bid_size", "bid", "ask", "ask_size", "last",
                "change", "open", "high", "low", "previous_close", 
                "turnover", "volume", 'operations', 'datetime'
            ])
        df = df.set_index('symbol')
        self.securities = df

    # --------------------------------------------------
    def get_data(self):

        self.hb.online.connect()
        self.hb.online.subscribe_options()
        self.hb.online.subscribe_securities('bluechips', '48hs')                       # Acciones del Panel lider - 48hs
        self.hb.online.subscribe_securities('bluechips', '24hs')                       # Acciones del Panel lider - 24hs
        self.hb.online.subscribe_securities('bluechips', 'SPOT')                       # Acciones del Panel lider - Contado Inmediato
        self.hb.online.subscribe_securities('government_bonds', '48hs')                # Bonos - 48hs
        # self.hb.online.subscribe_securities('government_bonds', '24hs')              # Bonos - 24hs
        self.hb.online.subscribe_securities('government_bonds', 'SPOT')                # Bonos - Contado Inmediato
        self.hb.online.subscribe_securities('cedears', '48hs')                         # CEDEARS - 48hs
        # self.hb.online.subscribe_securities('cedears', '24hs')                       # CEDEARS - 24hs
        # self.hb.online.subscribe_securities('cedears', 'SPOT')                       # CEDEARS - Contado Inmediato
        self.hb.online.subscribe_securities('general_board', '48hs')                   # Acciones del Panel general - 48hs
        # self.hb.online.subscribe_securities('general_board', '24hs')                 # Acciones del Panel general - 24hs
        # self.hb.online.subscribe_securities('general_board', 'SPOT')                 # Acciones del Panel general - Contado Inmediato
        self.hb.online.subscribe_securities('short_term_government_bonds', '48hs')     # LETRAS - 48hs
        # self.hb.online.subscribe_securities('short_term_government_bonds', '24hs')   # LETRAS - 24hs
        # self.hb.online.subscribe_securities('short_term_government_bonds', 'SPOT')   # LETRAS - Contado Inmediato
        self.hb.online.subscribe_securities('corporate_bonds', '48hs')                 # Obligaciones Negociables - 48hs
        # self.hb.online.subscribe_securities('corporate_bonds', '24hs')               # Obligaciones Negociables - 24hs
        # self.hb.online.subscribe_securities('corporate_bonds', 'SPOT')               # Obligaciones Negociables - Contado Inmediato
        self.hb.online.subscribe_repos()

        # Referencias:

        # bluechips = Acciones del Panel Lider
        # goverment_bonds = Bonos
        # general_board = Acciones del Panel General
        # short_term_government_bonds = Letras
        # corporate_bonds = Obligaciones Negociables

        while True:
            try:
                self.print_tibble()
                time.sleep(2) #update cada 2 SEGUNDOS

            except:
                print('Hubo un ERROR')

    # --------------------------------------------------
    def print_tibble(self):
        print(PrintTibble(self.securities))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get daily symbol data from HomeBroker',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-i', '--id_broker', 
        metavar = 'id_broker',
        default = '',
        type=str,
        help = "id_broker to log with HomeBroker")

    parser.add_argument(
        '-d', '--dni', 
        metavar = 'dni',
        default = '',
        type=str,
        help = "dni to log in HomeBroker")

    parser.add_argument(
        '-u', '--user', 
        metavar = 'User',
        default = '',
        type=str,
        help = "User to log in HomeBroker")

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in HomeBroker")

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    json_path = dir_path + '/cocos.json'
    
    if args.id_broker != '' and args.user != '' and args.password != '' and args.dni != '':
        hb = LivePrice(
            id_broker = args.id_broker, dni = args.dni, 
            user = args.user, password = args.password
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                hb = LivePrice(
                    id_broker = data_json['broker'], dni = data_json['dni'], 
                    user = data_json['user'], password = data_json['password']
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    # test = LivePrice()
    # test.print_tibble()

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_homebroker.live_price