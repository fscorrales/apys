#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Source: https://github.com/crapher/pyhomebroker
Purpose: Log to HomeBroker
Require package: 
    -   pip install pyhomebroker
    -   pip install pyhomebroker --upgrade --no-cache-dir
"""

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
from pyhomebroker import HomeBroker

# --------------------------------------------------
@dataclass
class HomeBrokerLogin():
    """
    Log to HomeBroker
    """
    id_broker: str = field(init=True, repr=False)
    dni: str = field(init=True, repr=False)
    user: str = field(init=True, repr=False)
    password: str = field(init=True, repr=False)
    hb: HomeBroker = field(init=False, repr=True)

    # --------------------------------------------------
    def __post_init__(self):
        self.login()

    # --------------------------------------------------
    def login(self):
        self.hb = HomeBroker(
            int(self.id_broker), on_options = self.on_options, 
            on_securities = self.on_securities, on_repos = self.on_repos, 
            on_error = self.on_error
            )
        self.hb.auth.login(
            dni = self.dni, user = self.user, 
            password = self.password, raise_exception = True
            )

    # --------------------------------------------------
    def on_options(self, online, quotes):
        """
        Event triggered when a new quote is received 
        from the options board
        """
        thisData = quotes
        thisData = thisData.drop(['expiration', 'strike', 'kind'], axis=1)
        thisData['change'] = thisData["change"] / 100
        thisData['datetime'] = pd.to_datetime(thisData['datetime'])
        thisData = thisData.rename(columns={"bid_size": "bidsize", "ask_size": "asksize"})
        self.options.update(thisData)
        #self.securities.update(thisData)

    # --------------------------------------------------
    def on_securities(self, online, quotes):
        """
        Event triggered when a new quote is received from 
        any of the supported security boards (NOT options)
        """
        #print(quotes)
        thisData = quotes
        thisData = thisData.reset_index()
        thisData['symbol'] = thisData['symbol'] + ' - ' +  thisData['settlement']
        thisData = thisData.drop(["settlement"], axis=1)
        thisData = thisData.set_index("symbol")
        thisData['change'] = thisData["change"] / 100
        thisData['datetime'] = pd.to_datetime(thisData['datetime'])
        self.securities.update(thisData)

    # --------------------------------------------------
    def on_repos(self, online, quotes):
        """
        Event triggered when a new quote is received 
        from the repos board (a.k.a 'cauciones')
        """
        pass
        # global cauciones
        # thisData = quotes
        # thisData = thisData.reset_index()
        # thisData = thisData.set_index("symbol")
        # thisData = thisData[['PESOS' in s for s in quotes.index]]
        # thisData = thisData.reset_index()
        # thisData['settlement'] = pd.to_datetime(thisData['settlement'])
        # thisData = thisData.set_index("settlement")
        # thisData['last'] = thisData["last"] / 100
        # thisData['bid_rate'] = thisData["bid_rate"] / 100
        # thisData['ask_rate'] = thisData["ask_rate"] / 100
        # thisData = thisData.drop(['open', 'high', 'low', 'volume', 'operations', 'datetime'], axis=1)
        # thisData = thisData[['last', 'turnover', 'bid_amount', 'bid_rate', 'ask_rate', 'ask_amount']]
        # cauciones.update(thisData)

    # --------------------------------------------------
    def on_error(self, online, error):
        print("Error Message Received: {0}".format(error))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Log to HomeBroker',
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
        hb = HomeBrokerLogin(
            id_broker = args.id_broker, dni = args.dni, 
            user = args.user, password = args.password
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                hb = HomeBrokerLogin(
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
    
    print(hb)

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_homebroker.homebroker_login