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
from .homebroker_login import HomeBrokerLogin

from ..utils.pydyverse import PrintTibble

# --------------------------------------------------
@dataclass
class LivePrice(HomeBrokerLogin):
    """
    Get constant datafrom HomeBroker
    """
    symbols_security: list = None
    symbols_option: list = None
    securities: pd.DataFrame = field(init=False, repr=False)
    options: pd.DataFrame = field(init=False, repr=False)

    # --------------------------------------------------
    def __post_init__(self):
        self.login()
        if self.symbols_security != None:
            self.init_securities(self.symbols_security)
        if self.symbols_option != None:
            self.init_options(self.symbols_option)
        if self.symbols_security != None or self.symbols_option != None:
            self.get_data()

    # --------------------------------------------------
    def init_securities(self, symbols:list) -> pd.DataFrame:
        settlement = [' - 48hs', ' - 24hs', ' - spot']
        symbols_settlement = [x + y for x in symbols for y in settlement]
        df = pd.DataFrame(
            {'symbol' : symbols_settlement},
            columns=[
                "symbol", "bid_size", "bid", "ask", "ask_size", "last",
                "change", "open", "high", "low", "previous_close", 
                "turnover", "volume", 'operations', 'datetime'
            ])
        df = df.set_index('symbol')
        self.securities = df

    # --------------------------------------------------
    def init_options(self, symbols:list) -> pd.DataFrame:
        df = pd.DataFrame(
            {'symbol' : symbols},
            columns=[
                "symbol", "bid_size", "bid", "ask", "ask_size", "last",
                "change", "open", "high", "low", "previous_close", 
                "turnover", "volume", 'operations', 'datetime'
            ])
        df = df.set_index('symbol')
        self.options = df
        # if self.symbols_security != None:
        #     self.securities = pd.concat([self.securities, self.options])
        # else:
        #     self.securities = self.options
        

    # --------------------------------------------------
    def get_data(self):

        self.hb.online.connect()
        
        if self.symbols_option != None:
            self.hb.online.subscribe_options()
        
        if self.symbols_security != None:
            self.hb.online.subscribe_securities('bluechips', '48hs')
            self.hb.online.subscribe_securities('bluechips', '24hs')
            self.hb.online.subscribe_securities('bluechips', 'SPOT')
            self.hb.online.subscribe_securities('government_bonds', '48hs')
            # self.hb.online.subscribe_securities('government_bonds', '24hs')
            self.hb.online.subscribe_securities('government_bonds', 'SPOT')
            self.hb.online.subscribe_securities('cedears', '48hs')
            # self.hb.online.subscribe_securities('cedears', '24hs')
            # self.hb.online.subscribe_securities('cedears', 'SPOT')
            self.hb.online.subscribe_securities('general_board', '48hs')
            # self.hb.online.subscribe_securities('general_board', '24hs')
            # self.hb.online.subscribe_securities('general_board', 'SPOT')
            self.hb.online.subscribe_securities('short_term_government_bonds', '48hs')
            # self.hb.online.subscribe_securities('short_term_government_bonds', '24hs')
            # self.hb.online.subscribe_securities('short_term_government_bonds', 'SPOT')
            self.hb.online.subscribe_securities('corporate_bonds', '48hs')
            # self.hb.online.subscribe_securities('corporate_bonds', '24hs')
            # self.hb.online.subscribe_securities('corporate_bonds', 'SPOT')
        
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
                time.sleep(15) #update cada 2 SEGUNDOS
            except:
                print('Hubo un ERROR')

    # --------------------------------------------------
    def print_tibble(self):
        print(PrintTibble(self.options))

    # # Cauciones
    # i = 1
    # fechas = []
    # while i < 31:
    #     fecha = date.today() + timedelta(days=i)
    #     fechas.extend([fecha])
    #     i += 1

    # cauciones = pd.DataFrame({'settlement':fechas}, columns=['settlement','last', 'turnover', 'bid_amount', 'bid_rate', 'ask_rate', 'ask_amount'])
    # cauciones['settlement'] = pd.to_datetime(cauciones['settlement'])
    # cauciones = cauciones.set_index('settlement')

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get daily symbol data from HomeBroker',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--securities', 
        metavar = 'securities',
        nargs='*',
        default = None,
        type=str,
        help = "List of securities to get live price")

    parser.add_argument(
        '-o', '--options', 
        metavar = 'options',
        nargs='*',
        default = None,
        type=str,
        help = "List of options to get live price")

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
        id_broker = args.id_broker
        user = args.user
        password = args.password
        dni = args.dni
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                id_broker = data_json['broker']
                user = data_json['user']
                password = data_json['password']
                dni = data_json['dni']
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    live_price = LivePrice(
        id_broker = id_broker, dni = dni, 
        user = user, password = password,
        symbols_security = args.securities,
        symbols_option = args.options
    )

    # live_price.get_data()
    # while True:
    #     try:
    #         live_price.print_tibble()
    #         time.sleep(15) #update
    #     except:
    #         print('Hubo un ERROR')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_homebroker.live_price -s GGAL COME -o GFGC440.AB