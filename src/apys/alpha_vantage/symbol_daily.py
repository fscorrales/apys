#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get daily symbol data from AlphaVantage
"""

import argparse
import datetime as dt
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
import requests
from datar import base, dplyr, f, tidyr

from ..utils.pydyverse import PrintTibble
from ..utils.validation import valid_date
from ..utils.sql_utils import SQLUtils
# from ..models.iol_model import IOLModel
from .alpha_vantage_login import AlphaVantage


# --------------------------------------------------
@dataclass
class SymbolDaily(SQLUtils):
    """
    Get daily symbol data from IOL
    :param IOL must be initialized first
    """
    alpha: AlphaVantage
    symbol: str
    size: str = 'compact'
    subset: str = 'Time Series (Daily)'
    output_df: bool = True
    df: pd.DataFrame = field(init=False, repr=False)
    # _TABLE_NAME:str = field(init=False, repr=False, default='symbol_daily')
    # _INDEX_COL:str = field(init=False, repr=False, default='id')
    # _FILTER_COL:str = field(init=False, repr=False, default='symbol')
    # _SQL_MODEL:IOLModel = field(init=False, repr=False, default=IOLModel)

    def __post_init__(self):
        self.getData()
        if self.output_df == True:
            self.toDataFrame()

    def getData(self):
        function = 'TIME_SERIES_DAILY'
        params = {
        'function':function, 'symbol':self.symbol,
        'outputsize':self.size
        }
        data = self.alpha._get("", params=params)

        if self.subset != None:
            data = data[self.subset]

        self.df = data
        return self.df

    def toDataFrame(self):
        df = pd.DataFrame.from_dict(self.df, orient = 'index')
        df = df.astype('float')
        df.index.name = 'date'
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df = df.sort_values('date', ascending = True)
        df.index = pd.to_datetime(df.index)
        self.df = df
        return self.df    

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get daily symbol data from AlphaVantage',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'symbol', 
        metavar = 'Symbol',
        type=str,
        help = "Symbol to look up")

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in ALphaVantage")

    # parser.add_argument(
    #     '-m', '--market', 
    #     metavar = 'Market',
    #     default = 'bCBA',
    #     type=str,
    #     help = "Market to look in")

    # parser.add_argument(
    #     '-a', '--adjusted', 
    #     metavar = 'Price adjustement',
    #     default = False,
    #     type=bool,
    #     help = "Should price be adjusted")

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    json_path = dir_path + '/credentials.json'
    if args.password != '':
        alpha = AlphaVantage(api_key = args.password)
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                alpha = AlphaVantage(
                    api_key = data_json['password'],
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    test = SymbolDaily(
        alpha = alpha,
        symbol = args.symbol,
        # market = args.market,
        # adjusted = args.adjusted
    )
    test.print_tibble()
    # test.to_sql(dir_path + '/iol.sqlite')

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.alpha_vantage.symbol_daily 'AAPL'

    # A tidy dataframe: 100 X 5
    #                 open      high       low     close      volume
                                                                
    # date       <float64> <float64> <float64> <float64>   <float64>
    # 2023-08-09    180.87  180.9300   177.010    178.19  60378492.0
    # 2023-08-10    179.48  180.7500   177.600    177.97  54686851.0
    # 2023-08-11    177.32  178.6200   176.550    177.79  52036672.0
    # 2023-08-14    177.97  179.6900   177.305    179.46  43675627.0
    # 2023-08-15    178.88  179.4800   177.050    177.45  43622593.0
    # 2023-08-16    177.13  178.5400   176.500    176.57  46964857.0
    # 2023-08-17    177.14  177.5054   173.480    174.00  66062882.0
    # 2023-08-18    172.30  175.1000   171.960    174.49  61172150.0
    # 2023-08-21    175.07  176.1300   173.735    175.84  46311879.0
    # 2023-08-22    177.06  177.6800   176.250    177.23  42084245.0
    # #... with 90 more rows