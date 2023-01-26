#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscorrales@gmail.com>
Source: https://github.com/crapher/pyhomebroker
Purpose: Get history daily data from HomeBroker
Require package: 
    -   pip install pyhomebroker
    -   pip install pyhomebroker --upgrade --no-cache-dir
"""

import argparse
import datetime as dt
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
from ..utils.pydyverse import PrintTibble
from .homebroker_login import HomeBrokerLogin

# --------------------------------------------------
@dataclass
class SymbolDaily(HomeBrokerLogin):
    """
    Get daily symbol data from HomeBroker
    """
    symbol: str
    from_date: dt.date
    to_date: dt.date = dt.date.today()
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.login()
        self.get_data()

    def get_data(self):

        # from_date = dt.datetime.strftime(self.from_date, "%Y-%m-%d")
        # to_date = dt.datetime.strftime(self.to_date, "%Y-%m-%d")

        df = self.hb.history.get_daily_history(
            self.symbol, self.from_date, self.to_date)
        self.df = pd.DataFrame(df)

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get history daily data from HomeBroker',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'symbol', 
        metavar = 'Symbol',
        type=str,
        help = "Symbol to look up")

    parser.add_argument(
        'from_date', 
        metavar = 'from_date',
        # type=valid_date,
        help = "The Start Date - format DD-MM-YYYY")

    parser.add_argument(
        '-to', '--to_date', 
        metavar = 'to_date',
        default = dt.datetime.strftime(dt.date.today(), "%d-%m-%Y"),
        # type=valid_date,
        help = "The End Date - format DD-MM-YYYY")

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
    
    if isinstance(args.from_date, str):
        from_date = dt.datetime.strptime(args.from_date, '%d-%m-%Y').date()
    if isinstance(args.to_date, str):
        to_date = dt.datetime.strptime(args.to_date, '%d-%m-%Y').date()

    if args.id_broker != '' and args.user != '' and args.password != '' and args.dni != '':
        test = SymbolDaily(
            id_broker = args.id_broker, dni = args.dni, 
            user = args.user, password = args.password,
            symbol = args.symbol, from_date = from_date,
            to_date = to_date,
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                test = SymbolDaily(
                    id_broker = data_json['broker'], dni = data_json['dni'], 
                    user = data_json['user'], password = data_json['password'],
                    symbol = args.symbol, from_date = from_date,
                    to_date = to_date,
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    test.print_tibble()

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_homebroker.symbol_daily GGAL 01-10-2022