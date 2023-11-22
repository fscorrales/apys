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
from pprint import pprint

import pandas as pd

from ..utils.handling_files import HandlingFiles
from ..utils.pydyverse import PrintTibble
from .instruments_list import InstrumentsList
from .pyrofex_login import PyRofexLogin
import pyRofex


# --------------------------------------------------
@dataclass
class WebsocketMarketData(PyRofexLogin, HandlingFiles):
    """
    The code show how to get different market data for an instrument and
    how to get historical trade data using pyRofex.
    """
    tickers: list = None
    instruments_formatted: list = field(init=False, repr=False)
    prices: pd.DataFrame = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.copy_dependencies()
        self.initialize()
        self.getInstrumentsFormatted()
        self.initWebsocketConnection()
        self.getData()
    
    def getInstrumentsFormatted(self, instruments_formatted:list = None) -> list:
        if instruments_formatted == None:
            instruments_formatted = [
                f'MERV - XMEV - {ticker} - CI' for ticker in self.tickers
            ]
            instruments_formatted.extend([
                f'MERV - XMEV - {ticker} - 48hs' for ticker in self.tickers
            ])
            instruments_formatted.extend([
                f'MERV - XMEV - {ticker} - 24hs' for ticker in self.tickers
            ])

        instruments_raw = self.aux.get_all_instruments()['instruments']
        all_instruments = {
            instrument_dict['instrumentId']['symbol'] 
            for instrument_dict in instruments_raw 
            if instrument_dict['instrumentId']['symbol'].split(' - ')[0] == 'MERV'
        }

        instruments_to_be_removed = [
            instrument 
            for instrument in instruments_formatted 
            if instrument not in all_instruments
        ]

        if instruments_to_be_removed:
            print("Instruments not found in the API's instrument list:")
            for instrument in instruments_to_be_removed:
                print(instrument)
                instruments_formatted.remove(instrument)
        else:
            print("\nAll instruments to be subscribed are in the API's instrument list\n")

        self.prices = pd.DataFrame(
            columns=[
                "bid_size", "bid", "ask", "ask_size", "last", 
                "last_size", 'nominal_volume', 'effective_volume'
            ], 
            index=instruments_formatted
        )
        self.prices = self.prices.fillna(0)
        self.prices.index.name = "instrument"
        self.instruments_formatted = instruments_formatted
        return instruments_formatted

    # 2-Defines the handlers that will process the messages and exceptions.
    # --------------------------------------------------
    def marketDataHandler(self, message):
        # print("Market Data Message Received: {0}".format(message))
        # global prices, msg_date_time

        # print(f"Market data received for {message['instrumentId']['symbol'].replace('MERV - XMEV - ', '')} at "
        #       f"{datetime.fromtimestamp(message['timestamp']/1000)}")

        # msg_datetime = dt.datetime.fromtimestamp(message['timestamp'] / 1000)
        # msg_date_time = msg_datetime.strftime("%m/%d/%Y %H:%M:%S")
        # msg_time_time = msg_datetime.time()

        if message['marketData']['LA']:
            self.prices.loc[message['instrumentId']['symbol'], 'last'] = message['marketData']['LA']['price']
            self.prices.loc[message['instrumentId']['symbol'], 'last_size'] = message['marketData']['LA']['size']
        else:
            self.prices.loc[message['instrumentId']['symbol'], 'last'] = 0
            self.prices.loc[message['instrumentId']['symbol'], 'last_size'] = 0

        if message['marketData']['OF']:
            self.prices.loc[message['instrumentId']['symbol'], 'ask'] = message['marketData']['OF'][0]['price']
            self.prices.loc[message['instrumentId']['symbol'], 'ask_size'] = message['marketData']['OF'][0]['size']
        else:
            self.prices.loc[message['instrumentId']['symbol'], 'ask'] = 0
            self.prices.loc[message['instrumentId']['symbol'], 'ask_size'] = 0

        if message['marketData']['BI']:
            self.prices.loc[message['instrumentId']['symbol'], 'bid'] = message['marketData']['BI'][0]['price']
            self.prices.loc[message['instrumentId']['symbol'], 'bid_size'] = message['marketData']['BI'][0]['size']
        else:
            self.prices.loc[message['instrumentId']['symbol'], 'bid'] = 0
            self.prices.loc[message['instrumentId']['symbol'], 'bid_size'] = 0

        if message['marketData']['NV']:
            self.prices.loc[message['instrumentId']['symbol'], 'nominal_volume'] = message['marketData']['NV']
        else:
            self.prices.loc[message['instrumentId']['symbol'], 'nominal_volume'] = 0

        if message['marketData']['EV']:
            self.prices.loc[message['instrumentId']['symbol'], 'effective_volume'] = message['marketData']['EV']
        else:
            self.prices.loc[message['instrumentId']['symbol'], 'effective_volume'] = 0

    # --------------------------------------------------
    def orderReportHandler(self, message):
        print("Order Report Message Received: {0}".format(message))
    # --------------------------------------------------
    def errorHandler(self, message):
        print(f"\n>>>>>>Error message received at {dt.datetime.now()}:")
        pprint(message)
        pyRofex.close_websocket_connection()
        quit()
        # print("Error Message Received: {0}".format(message))
    # --------------------------------------------------
    def exceptionHandler(self, e):
        print(f"\n>>>>>>Exception occurred at {dt.datetime.now()}:")
        pprint(e.message)
        pyRofex.close_websocket_connection()
        quit()
        # print("Exception Occurred: {0}".format(e.message))

    # 3-Initiate Websocket Connection
    # --------------------------------------------------
    def initWebsocketConnection(self):
        pyRofex.init_websocket_connection(
            market_data_handler=self.marketDataHandler,
            # order_report_handler=self.order_report_handler,
            error_handler=self.errorHandler,
            exception_handler=self.exceptionHandler
        )
        print("Websocket connection successfully initialized for:")
        index_list = [item.replace('MERV - XMEV - ', '') for item in self.instruments_formatted]
        index_list = ['Ticker - Plazo'] + index_list
        index_list = [[el] for el in index_list]
        pprint(index_list)

    def getData(self):
        
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

        num_parts = len(self.instruments_formatted) // 1000 + 1
        part_size = len(self.instruments_formatted) // num_parts
        parts = [self.instruments_formatted[i:i+part_size] for i in range(0, len(self.instruments_formatted), part_size)]
        for x in parts:
            pyRofex.market_data_subscription(
                tickers=x,
                entries=entries
            )
        # half_list = round(len(self.instruments_formatted)/2)
        # for x in [self.instruments_formatted[:half_list], self.instruments_formatted[half_list:]]:
        #     pyRofex.market_data_subscription(
        #         tickers=x,
        #         entries=entries
        #     )
        
        while True:
            try:
                # Panel.update('D1', msg_date_time)
                # Panel.update('B2', [prices.columns.tolist()] + prices.values.tolist())
                self.prices.to_excel('prices.xlsx')
            except:
                pass
            time.sleep(1)

    def forTestOnly(self):
        print(f"Número de Instrumentos: {len(self.instruments_formatted)}")
        num_parts = len(self.instruments_formatted) // 1000 + 1
        print(f"Número de Partes a dividir: {num_parts}")
        part_size = len(self.instruments_formatted) // num_parts
        print(f"Tamaño de cada parte: {part_size}")
        parts = [self.instruments_formatted[i:i+part_size] for i in range(0, len(self.instruments_formatted), part_size)]
        for x in parts:
            print(x)
        # half_list = round(len(self.instruments_formatted)/2)
        # for x in [self.instruments_formatted[:half_list], self.instruments_formatted[half_list:]]:
        #     print(x)

    def printTibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def getArgs():
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
        default = '', #DLR/ENE24
        type=str,
        help = "Get tickers's data")
    
    parser.add_argument('--to_excel', action='store_true')
    parser.add_argument('--no-to_excel', dest='to_excel', action='store_false')
    parser.set_defaults(to_excel=False)

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = getArgs()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if args.live:
        json_path = dir_path + '/live.json'
    else:
        json_path = dir_path + '/remarkets.json'

    if args.user != '' and args.password != '' and args.dni != '' and args.account != '':
        user = args.user
        password = args.password
        account = args.account    
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                user = data_json['user']
                password = data_json['password']
                account = data_json['account']   
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    if args.tickers == '':
        # with open(os.path.join(dir_path, "Tickers.txt"), "r") as file:
        #     tickers_list = file.read().splitlines()
        tickers_list = InstrumentsList(
            user = user, password = password,
            account = account, live=args.live
        ).getCedearsFromInstruments()
    else:
        tickers_list = args.tickers

    test = WebsocketMarketData(
        user = user, password = password,
        account = account, live=args.live,
        tickers=tickers_list
    )

    # test.forTestOnly()

    if args.to_excel:
        test.to_excel(dir_path + '/websocket_market_data.xlsx')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_pyrofex.websocket_market_data --live
    # python -m apys.my_pyrofex.websocket_market_data --live -t 'GGAL'