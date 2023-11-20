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

# import openpyxl
import pandas as pd

from ..utils.pydyverse import PrintTibble
from ..utils.handling_files import HandlingFiles
from .pyrofex_login import PyRofexLogin


# --------------------------------------------------
@dataclass
class InstrumentsList(HandlingFiles):
    """
    The code show how to work with instruments data using pyRofex
    """
    pyrofex: PyRofexLogin
    details: bool = field(init=True, repr=False, default=False)
    ticker: str = field(init=True, repr=False, default='')
    instruments: list = field(init=False, repr=False, default_factory=list)
    letters: list = field(init=False, repr=False)
    bonds: list = field(init=False, repr=False)
    on: list = field(init=False, repr=False)
    cedears: list = field(init=False, repr=False)
    stocks: list = field(init=False, repr=False)
    indexes: list = field(init=False, repr=False)
    caucions: list = field(init=False, repr=False)
    options: list = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.letter_cficode  = 'DYXTXR'
        self.bond_cficode  = 'DBXXXX'
        self.on_cficode = 'DBXXFR'
        self.cedear_cficode = 'EMXXXX'
        self.stock_cficode = 'ESXXXX'
        self.index_cficode = 'MRIXXX'
        self.caucion_cficode = 'RPXXXX'
        self.call_cficode  = 'OCASPS'
        self.put_cficode  = 'OPASPS'
        # self.copy_dependencies()
        # self.initialize()
        self.get_data()

    def get_data(self):
        if self.details:
            if self.ticker == '':
                df = self.pyrofex.aux.get_detailed_instruments()
            else:
                df = self.pyrofex.aux.get_instrument_details(ticker=self.ticker)
        else:
            df = self.pyrofex.aux.get_all_instruments()
        df = df['instruments']
        self.df = pd.DataFrame(df)

    def setToday(self):
        today = dt.date.today()
        today_yearmonthday = today.strftime('%Y%m%d')
        return today_yearmonthday
    
    def getInstruments(self):
        self.instruments = self.pyrofex.aux.get_detailed_instruments()['instruments']
        return self.instruments

    def getLettersFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        letters = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.letter_cficode)
        self.letters = sorted(list(set(letters)))
        return self.letters
    
    def getBondsFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        bonds = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.bond_cficode)
        self.bonds = sorted(list(set(bonds)))
        return self.bonds
    
    def getONFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        on = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.on_cficode)
        self.on = sorted(list(set(on)))
        return self.on
    
    def getCedearsFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        cedears = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.cedear_cficode)
        self.cedears = sorted(list(set(cedears)))
        return self.cedears
    
    def getStocksFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        stocks = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.stock_cficode)
        self.stocks = sorted(list(set(stocks)))
        return self.stocks

    def getIndexesFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        indexes = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.index_cficode)
        self.indexes = sorted(list(set(indexes)))
        return self.indexes

    def getCaucionesFromInstruments(self):
        if len(self.instruments) == 0:
            self.getInstruments()
        cauciones = (instrument['securityDescription'].split(' - ')[2] 
                   for instrument in self.instruments 
                   if instrument['cficode'] == self.caucion_cficode)
        self.cauciones = sorted(list(set(cauciones)))
        return self.cauciones
        
    def getOptionsFromInstruments(self, 
                                     underlying_keywords:list = ["Galicia", "Comercial", "YPF Merval"]) -> list:
        if len(self.instruments) == 0:
            self.getInstruments()
        vencimientos = []
        opciones = []

        vencimientos = ([instrument['maturityDate'] 
                         for instrument in self.instruments 
                            if instrument['cficode'] == self.call_cficode 
                            or instrument['cficode'] == self.put_cficode 
                            and "Galicia" in instrument['underlying']])
        vencimientos = list(set(vencimientos))
        vencimientos.sort()
        vencimientos = [x for x in vencimientos if x >= self.setToday()]

        opciones = [instrument['securityDescription'].split(' - ')[2] 
                    for instrument in self.instruments 
                    if instrument['cficode'] in [self.call_cficode, self.put_cficode] 
                    and any(keyword in instrument['underlying'] for keyword in underlying_keywords) 
                    and instrument['maturityDate'] in vencimientos[:2]]

        self.options = sorted(list(set(opciones)))
        
        return self.options

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
        pyrofex = PyRofexLogin(
            user = args.user, password = args.password,
            account = args.account, live=args.live,
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                pyrofex = PyRofexLogin(
                    user = data_json['user'], password = data_json['password'],
                    account = data_json['account'], live=args.live,
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    # test.print_tibble()
    test = InstrumentsList(
        pyrofex=pyrofex,
        details=args.details,
        ticker=args.ticker
    )
    print(test.getLettersFromInstruments())
    if args.to_excel:
        test.to_excel(dir_path + '/instruments.xlsx')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.my_pyrofex.instruments_list --live
    # python -m apys.my_pyrofex.instruments_list --live --details --to_excel