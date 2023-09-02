#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Source: https://github.com/matbarofex/pyRofex
Purpose: Get market data using websocket API.
Require package: 
    -   pip install pyRofex
"""

import argparse
import datetime as dt
import inspect
import json
import os
import sys
import time
from dataclasses import dataclass, field

import pandas as pd

from ..utils.handling_files import HandlingFiles
from ..utils.pydyverse import PrintTibble
from .pyrofex_login import PyRofexLogin

# --------------------------------------------------
@dataclass
class WebsocketMarketData(PyRofexLogin, HandlingFiles):
    """
    The code show how to get different market data for an instrument and
    how to get historical trade data using pyRofex.
    """
    tickers: list = None
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.copy_dependencies()
        if self.live:
            self.set_websocket()
        self.initialize()
        self.init_websocket_connection()
        self.get_data()

    def get_data(self):
        
        entries = [
            self.aux.MarketDataEntry.BIDS,
            self.aux.MarketDataEntry.OFFERS,
            self.aux.MarketDataEntry.LAST,
            # self.aux.MarketDataEntry.CLOSING_PRICE,
            # self.aux.MarketDataEntry.OPENING_PRICE,
            # self.aux.MarketDataEntry.HIGH_PRICE,
            # self.aux.MarketDataEntry.LOW_PRICE,
            # self.aux.MarketDataEntry.SETTLEMENT_PRICE,
            self.aux.MarketDataEntry.NOMINAL_VOLUME,
            self.aux.MarketDataEntry.TRADE_EFFECTIVE_VOLUME,
            # self.aux.MarketDataEntry.TRADE_VOLUME,
            # self.aux.MarketDataEntry.OPEN_INTEREST
        ]
        while True:
            self.market_data_subscription(tickers=self.tickers, entries=entries)
            # self.df = pd.DataFrame(df)
            # self.print_tibble()
            time.sleep(1)
        # time.sleep(5)
        # self.aux.close_websocket_connection()

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Log to pyRofex',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-u', '--user', 
        metavar = 'User',
        default = '',
        type=str,
        help = "User to log in pyRofex")

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in pyRofex")
    
    parser.add_argument(
        '-a', '--account', 
        metavar = 'account',
        default = '',
        type=str,
        help = "Account to log in pyRofex")
    
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--no-live', dest='live', action='store_false')
    parser.set_defaults(live=False)

    parser.add_argument(
        '-t', '--tickers',
        nargs='*', 
        metavar = 'tickers',
        default = 'DLR/ENE24',
        type=str,
        help = "Get tickers's data")
    
    parser.add_argument('--to_excel', action='store_true')
    parser.add_argument('--no-to_excel', dest='to_excel', action='store_false')
    parser.set_defaults(to_excel=False)

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if args.live:
        json_path = dir_path + '/live.json'
    else:
        json_path = dir_path + '/remarkets.json'
    
    print(args.tickers)

    if args.user != '' and args.password != '' and args.dni != '' and args.account != '':
        test = WebsocketMarketData(
            user = args.user, password = args.password,
            account = args.account, live=args.live,
            tickers=args.tickers
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                test = WebsocketMarketData(
                    user = data_json['user'], password = data_json['password'],
                    account = data_json['account'], live=args.live,
                    tickers=args.tickers
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    if args.to_excel:
        test.to_excel(dir_path + '/websocket_market_data.xlsx')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_pyrofex.websocket_market_data --live --tickers 'MERV - XMEV - GGAL - 48hs'