#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Source: https://finnhub.io/docs/api/websocket-trades
Purpose: Get market data using Finnhub websocket API.
Require package: 
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
import websocket


# --------------------------------------------------
@dataclass
class WebsocketMarketData(HandlingFiles):
    """
    The code show how to get different market data for an instrument and
    how to get historical trade data using pyRofex.
    """
    api_key: str
    tickers: list = None
    ws: websocket = field(init=False, repr=False)
    prices: pd.DataFrame = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.initialize()
        # self.getData()

    def initialize(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://ws.finnhub.io?token=" + self.api_key,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close
        )
        self.prices = pd.DataFrame(
            columns=[
                "last_price", "time", "volume"
            ], 
            index=self.tickers
        )
        self.prices = self.prices.fillna(0)
        self.prices.index.name = "symbol"

    # def on_message(self, message):
    #     try:
    #         message_dict = json.loads(message)
    #         print(type(message_dict['data']))
    #         # Ahora puedes explorar la estructura del diccionario message_dict
    #         for key, value in message_dict.items():
    #             print(f"Clave: {key}, Valor: {value}")  
    #     except json.JSONDecodeError:
    #         print("El mensaje no sigue una estructura JSON")

        # if message['data']:
        #     self.marketDataHandler(message)
        # print(message)

    def on_message(self, message):
        message_dict = json.loads(message)  # Convierte el mensaje en un diccionario
        data_list = message_dict.get('data')  # Accede a la lista bajo la clave 'data'
        # self.marketDataHandler(data_list)
        if data_list:  # Verifica que 'data_list' no sea None
            for data_dict in data_list:  # Itera a través de los diccionarios en la lista
                # Accede a los valores dentro de cada diccionario
                value1 = data_dict.get('s')
                value2 = data_dict.get('p')
                # Haz algo con los valores, por ejemplo, imprímelos
                print(f"Valor de key1: {value1}, Valor de key2: {value2}")
        else:
            print("La clave 'data' no está presente en el mensaje")

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def on_open(self):
        for ticker in self.tickers:
            self.ws.send(f'{{"type":"subscribe","symbol":"{ticker}"}}')
        # self.ws.send('{"type":"subscribe","symbol":"AAPL"}')
        # self.ws.send('{"type":"subscribe","symbol":"AMZN"}')
        # self.ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
        # self.ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

    def marketDataHandler(self, message):
        # print("Market Data Message Received: {0}".format(message))
        # global prices, msg_date_time

        # print(f"Market data received for {message['instrumentId']['symbol'].replace('MERV - XMEV - ', '')} at "
        #       f"{datetime.fromtimestamp(message['timestamp']/1000)}")

        # msg_datetime = dt.datetime.fromtimestamp(message['timestamp'] / 1000)
        # msg_date_time = msg_datetime.strftime("%m/%d/%Y %H:%M:%S")
        # msg_time_time = msg_datetime.time()

        if message['data']['p']:
            self.prices.loc[message['data']['s'], 'last_price'] = message['data']['s']['p']
        else:
            self.prices.loc[message['data']['s'], 'last_price'] = 0

        if message['data']['v']:
            self.prices.loc[message['data']['s'], 'volume'] = message['data']['s']['v']
        else:
            self.prices.loc[message['data']['s'], 'volume'] = 0

        # if message['marketData']['OF']:
        #     self.prices.loc[message['instrumentId']['symbol'], 'ask'] = message['marketData']['OF'][0]['price']
        #     self.prices.loc[message['instrumentId']['symbol'], 'ask_size'] = message['marketData']['OF'][0]['size']
        # else:
        #     self.prices.loc[message['instrumentId']['symbol'], 'ask'] = 0
        #     self.prices.loc[message['instrumentId']['symbol'], 'ask_size'] = 0

        # if message['marketData']['BI']:
        #     self.prices.loc[message['instrumentId']['symbol'], 'bid'] = message['marketData']['BI'][0]['price']
        #     self.prices.loc[message['instrumentId']['symbol'], 'bid_size'] = message['marketData']['BI'][0]['size']
        # else:
        #     self.prices.loc[message['instrumentId']['symbol'], 'bid'] = 0
        #     self.prices.loc[message['instrumentId']['symbol'], 'bid_size'] = 0

        # if message['marketData']['NV']:
        #     self.prices.loc[message['instrumentId']['symbol'], 'nominal_volume'] = message['marketData']['NV']
        # else:
        #     self.prices.loc[message['instrumentId']['symbol'], 'nominal_volume'] = 0

        # if message['marketData']['EV']:
        #     self.prices.loc[message['instrumentId']['symbol'], 'effective_volume'] = message['marketData']['EV']
        # else:
        #     self.prices.loc[message['instrumentId']['symbol'], 'effective_volume'] = 0

    def getData(self):
        self.ws.on_open = self.on_open
        self.ws.run_forever()
    
    def printTibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def getArgs():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Log to Finnhub',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in pyRofex")
    
    # parser.add_argument('--live', action='store_true')
    # parser.add_argument('--no-live', dest='live', action='store_false')
    # parser.set_defaults(live=False)

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
    json_path = dir_path + '/finnhub.json'

    if args.password != '':
        finnhub = WebsocketMarketData(
            api_key = args.password,
            tickers=args.tickers
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                finnhub = WebsocketMarketData(
                    api_key = data_json['password'],
                    tickers=args.tickers,
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} password ' +
                'as key does not exist in the directory, ' + 
                'it must be given.'
            )
            sys.exit(msg)

    finnhub.getData()

    # test.forTestOnly()

    # if args.to_excel:
    #     test.to_excel(dir_path + '/websocket_market_data.xlsx')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.finnhub.websocket_market_data -t AAPL AMZN 'BINANCE:BTCUSDT' 'IC MARKETS:1'
    # python -m apys.finnhub.websocket_market_data --to_excel -t 'AMZN'