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
from dataclasses import dataclass, field
import threading
import time
import signal

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
    print_console: bool = False
    ws: websocket = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.initialize()
        # self.getData()
        # Registrar el manejador de señales
    #     signal.signal(signal.SIGINT, self.signal_handler)
    #     signal.signal(signal.SIGTERM, self.signal_handler)

    # def signal_handler(self, sig, frame):
    #     # Cerrar el websocket
    #     self.ws.close()
    #     sys.exit(0)

    def initialize(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://ws.finnhub.io?token=" + self.api_key,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close
        )

        self.df = pd.DataFrame(
            columns=[
                "last_price",  "datetime", "volume"
            ], 
            index=self.tickers
        )
        self.df = self.df.fillna(0)
        self.df.index.name = "symbol"

    def startWebSocket(self):
        # Create a thread and target it to the run_forever function, then start it.
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.start()

    def on_message(self, message):
        message_dict = json.loads(message)  # Convierte el mensaje en un diccionario
        data_list = message_dict.get('data')  # Accede a la lista bajo la clave 'data'
        if data_list:  # Verifica que 'data_list' no sea None
            self.marketDataHandler(data_list)
        else:
            print("La clave 'data' no está presente en el mensaje")

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def on_open(self):
        for ticker in self.tickers:
            self.ws.send(f'{{"type":"subscribe","symbol":"{ticker}"}}')

    def marketDataHandler(self, message):
        for data_dict in message:  # Itera a través de los diccionarios en la lista
            # Accede a los valores dentro de cada diccionario
            self.df.loc[data_dict.get('s'), 'last_price']  = data_dict.get('p')
            self.df.loc[data_dict.get('s'), 'datetime']  = dt.datetime.utcfromtimestamp(data_dict.get('t') / 1000.0)
            self.df.loc[data_dict.get('s'), 'volume']  = data_dict.get('v')
        # if self.print_console:
        #     self.printTibble()

    def getData(self, seconds_to_update:int = 15):
        self.ws.on_open = self.on_open
        # self.ws.run_forever()
        self.startWebSocket()
        while True:
            time.sleep(seconds_to_update)
            if self.print_console:
                self.printTibble()
    
    def printTibble(self, data = None):
        if data is None:
            data = self.df
        print(PrintTibble(data))

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
    
    parser.add_argument('--print', action='store_true')
    parser.add_argument('--no-print', dest='print', action='store_false')
    parser.set_defaults(print=False)

    parser.add_argument(
        '-t', '--tickers',
        nargs='*', 
        metavar = 'tickers',
        default = '',
        type=str,
        help = "Get tickers's data")

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
            tickers=args.tickers,
            print_console=args.print
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                finnhub = WebsocketMarketData(
                    api_key = data_json['password'],
                    tickers=args.tickers,
                    print_console=args.print
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
    # python -m apys.finnhub.websocket_market_data --print -t AAPL AMZN 'BINANCE:BTCUSDT' 'IC MARKETS:1'