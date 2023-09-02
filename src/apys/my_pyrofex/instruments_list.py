#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Source: https://github.com/matbarofex/pyRofex
Purpose: Get instruments data using pyRofex
Require package: 
    -   pip install pyRofex
"""

import argparse
import datetime as dt
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import openpyxl
import pandas as pd

from ..utils.pydyverse import PrintTibble
from ..utils.handling_files import HandlingFiles
from .pyrofex_login import PyRofexLogin


# --------------------------------------------------
@dataclass
class InstrumentsList(PyRofexLogin, HandlingFiles):
    """
    The code show how to work with instruments data using pyRofex
    """
    details: bool = field(init=True, repr=False, default=False)
    ticker: str = field(init=True, repr=False, default='')
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.copy_dependencies()
        self.initialize()
        self.get_data()

    def get_data(self):
        
        if self.details:
            if self.ticker == '':
                df = self.aux.get_detailed_instruments()
            else:
                df = self.aux.get_instrument_details(ticker=self.ticker)
        else:
            df = self.aux.get_all_instruments()
        self.df = pd.DataFrame(df)

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

    parser.add_argument('--details', action='store_true')
    parser.add_argument('--no-details', dest='details', action='store_false')
    parser.set_defaults(details=False)

    parser.add_argument(
        '-t', '--ticker', 
        metavar = 'ticker',
        default = '',
        type=str,
        help = "Get ticker's detailed info")
    
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

    if args.user != '' and args.password != '' and args.dni != '' and args.account != '':
        test = InstrumentsList(
            user = args.user, password = args.password,
            account = args.account, live=args.live, 
            details=args.details, ticker=args.ticker
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                print(data_json['user'])
                print(data_json['password'])
                print(data_json['account'])
                test = InstrumentsList(
                    user = data_json['user'], password = data_json['password'],
                    account = data_json['account'], live=args.live,
                    details=args.details, ticker=args.ticker
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
    if args.to_excel:
        test.to_excel(dir_path + '/instruments.xlsx')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_pyrofex.instruments_list