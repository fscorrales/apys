#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Source: https://github.com/matbarofex/pyRofex
API Doc: https://apihub.primary.com.ar/assets/docs/Primary-API.pdf
Remarkets: https://remarkets.primary.ventures/
Purpose: Log to pyRofex
Require package: 
    -   pip install pyRofex
"""

import argparse
import inspect
import json
import os
import sys
import datetime as dt
from dataclasses import dataclass, field
from pprint import pprint

import pyRofex

# --------------------------------------------------
@dataclass
class PyRofexLogin():
    """
    Log to pyRofex
    :param user: the user used for authentication.
    :type user: str
    :param password: the password used for authentication.
    :type password: str
    :param account: user's default account.
    :type account: str
    :param live: live or remarkets environment. Default set to false (remarkets)
    :type live: bool
    """
    user: str = field(init=True, repr=False)
    password: str = field(init=True, repr=False)
    account: str = field(init=True, repr=False)
    live: bool = field(init=True, repr=False, default=False)
    url_live: str = field(init=True, repr=False, 
                          default='https://api.veta.xoms.com.ar/')
    ws_live: str = field(init=True, repr=False, 
                          default='wss://api.veta.xoms.com.ar/')

    # --------------------------------------------------
    def __post_init__(self):
        self.copy_dependencies()
        self.initialize()

    # 0-Copy dependencies from pyRofex
    # --------------------------------------------------
    def copy_dependencies(self):
        # self.Environment = pyRofex.Environment()
        # self.MarketDataEntry = pyRofex.MarketDataEntry()
        # self.Market = pyRofex.Market()
        # self.OrderType = pyRofex.OrderType()
        # self.Side = pyRofex.Side()
        # self.TimeInForce = pyRofex.TimeInForce()
        self.aux = pyRofex.service

    # 1-Initialize the environment
    # --------------------------------------------------
    def set_websocket(self, url:str = '', ws:str = ''):
        if url != '':
            self.url_live = url
        if ws != '':
            self.ws_live = ws
        # Configurar con la URL que corresponda al broker
        pyRofex._set_environment_parameter("url", self.url_live, pyRofex.Environment.LIVE) 
        # Configurar con el WS que corresponda al broker
        pyRofex._set_environment_parameter("ws", self.ws_live, pyRofex.Environment.LIVE) 
    # --------------------------------------------------
    def initialize(self):
        try:
            if self.live:
                pyRofex.initialize(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    environment=pyRofex.Environment.LIVE
                )
            else:
                pyRofex.initialize(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    environment=pyRofex.Environment.REMARKET
                )
        except pyRofex.components.exceptions.ApiException:
            print(f'\npyRofex environment could not be initialized. Authentication failed.'
                '\nCheck login credentials: Incorrect User or Password. (APIException)')
            quit()
        print(f'\npyRofex environment successfully initialized')

    # 2-Defines the handlers that will process the messages and exceptions.
    # --------------------------------------------------
    def market_data_handler(message):
        print("Market Data Message Received: {0}".format(message))
        # global prices, msg_date_time

        # print(f"Market data received for {message['instrumentId']['symbol'].replace('MERV - XMEV - ', '')} at "
        #       f"{datetime.fromtimestamp(message['timestamp']/1000)}")

        # msg_datetime = dt.datetime.fromtimestamp(message['timestamp'] / 1000)
        # msg_date_time = msg_datetime.strftime("%m/%d/%Y %H:%M:%S")
        # msg_time_time = msg_datetime.time()

        # if message['marketData']['LA']:
        #     prices.loc[message['instrumentId']['symbol'], 'Last'] = message['marketData']['LA']['price']
        #     prices.loc[message['instrumentId']['symbol'], 'Last_size'] = message['marketData']['LA']['size']
        # else:
        #     prices.loc[message['instrumentId']['symbol'], 'Last'] = 0
        #     prices.loc[message['instrumentId']['symbol'], 'Last_size'] = 0

        # if message['marketData']['OF']:
        #     prices.loc[message['instrumentId']['symbol'], 'Ask'] = message['marketData']['OF'][0]['price']
        #     prices.loc[message['instrumentId']['symbol'], 'Ask_size'] = message['marketData']['OF'][0]['size']
        # else:
        #     prices.loc[message['instrumentId']['symbol'], 'Ask'] = 0
        #     prices.loc[message['instrumentId']['symbol'], 'Ask_size'] = 0

        # if message['marketData']['BI']:
        #     prices.loc[message['instrumentId']['symbol'], 'Bid'] = message['marketData']['BI'][0]['price']
        #     prices.loc[message['instrumentId']['symbol'], 'Bid_size'] = message['marketData']['BI'][0]['size']
        # else:
        #     prices.loc[message['instrumentId']['symbol'], 'Bid'] = 0
        #     prices.loc[message['instrumentId']['symbol'], 'Bid_size'] = 0

        # if message['marketData']['NV']:
        #     prices.loc[message['instrumentId']['symbol'], 'Nominal_volume'] = message['marketData']['NV']
        # else:
        #     prices.loc[message['instrumentId']['symbol'], 'Nominal_volume'] = 0

        # if message['marketData']['EV']:
        #     prices.loc[message['instrumentId']['symbol'], 'Effective_volume'] = message['marketData']['EV']
        # else:
        #     prices.loc[message['instrumentId']['symbol'], 'Effective_volume'] = 0

    # --------------------------------------------------
    def order_report_handler(self, message):
        print("Order Report Message Received: {0}".format(message))
    # --------------------------------------------------
    def error_handler(self, message):
        # print(f"\n>>>>>>Error message received at {dt.datetime.now()}:")
        # pprint(message)
        # pyRofex.close_websocket_connection()
        # quit()
        print("Error Message Received: {0}".format(message))
    # --------------------------------------------------
    def exception_handler(self, e):
        # print(f"\n>>>>>>Exception occurred at {dt.datetime.now()}:")
        # pprint(e.message)
        # pyRofex.close_websocket_connection()
        # quit()
        print("Exception Occurred: {0}".format(e.message))

    # 3-Initiate Websocket Connection
    # --------------------------------------------------
    def init_websocket_connection(self):
        pyRofex.init_websocket_connection(
            market_data_handler=self.market_data_handler,
            # order_report_handler=self.order_report_handler,
            error_handler=self.error_handler,
            exception_handler=self.exception_handler
        )

    # 4-Subscribes to receive market data messages **
    # --------------------------------------------------
    def market_data_subscription(
            self, tickers:str = 'DLR/ENE24', 
            entries:[pyRofex.MarketDataEntry] = None
    ):
        # Tickers list to subscribe
        # tickers = ["DLR/DIC23", "DLR/ENE24"]
        # Uses the MarketDataEntry enum to define the entries we want to subscribe to
        if entries == None:
            entries = [
                pyRofex.MarketDataEntry.BIDS,
                pyRofex.MarketDataEntry.OFFERS,
                pyRofex.MarketDataEntry.LAST
            ]
        pyRofex.market_data_subscription(tickers=tickers, entries=entries)

    # 5-Subscribes to receive order report messages (default account will be used) **
    # --------------------------------------------------
    def order_report_subscription(self):
        pyRofex.order_report_subscription()

    # Auxiliary methods
    # --------------------------------------------------
    def get_detailed_instruments(self):
        pyRofex.get_detailed_instruments()

    def get_all_instruments(self):
        pyRofex.get_all_instruments()

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
    
    if args.user != '' and args.password != '' and args.dni != '' and args.account != '':
        pr = PyRofexLogin(
            user = args.user, password = args.password,
            account = args.account, live=args.live
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                pr = PyRofexLogin(
                    user = data_json['user'], password = data_json['password'],
                    account = data_json['account'], live=args.live
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_pyrofex.pyrofex_login