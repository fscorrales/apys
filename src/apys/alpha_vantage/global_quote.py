#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get daily symbol data from AlphaVantage

"""

import argparse
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
class GlobalQuote(SQLUtils):
    """
    Get daily symbol data from IOL
    :param IOL must be initialized first
    """
    alpha: AlphaVantage
    symbol: str
    subset: str = 'Global Quote'
    output_df: bool = True
    df: pd.DataFrame = field(init=False, repr=False)
    # _TABLE_NAME:str = field(init=False, repr=False, default='symbol_daily')
    # _INDEX_COL:str = field(init=False, repr=False, default='id')
    # _FILTER_COL:str = field(init=False, repr=False, default='symbol')
    # _SQL_MODEL:IOLModel = field(init=False, repr=False, default=IOLModel)

    def __post_init__(self):
        if isinstance(self.symbol, list):
            df_list = []
            for symbol in self.symbol:
                print(symbol)
                self.getData(symbol)
                self.toDataFrame()
                df_list.append(self.df)
            self.df = pd.concat(df_list)
        else:
            self.getData()
            if self.output_df == True:
                self.toDataFrame()

    def getData(self, symbol = None):
        function = 'GLOBAL_QUOTE'

        if symbol == None:
            symbol = self.symbol

        params = {
            'function':function, 'symbol':symbol,
        }

        data = self.alpha._get("", params=params)
        

        if self.subset != None:
            data = data[self.subset]

        self.df = data
        return self.df

    def toDataFrame(self):
        df = pd.DataFrame.from_dict(self.df, orient = 'index').transpose()
        df.columns = ['symbol', 'open', 'high', 'low', 'close', 'volume', 
        'date', 'previous_close', 'change', 'percent_change']
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
        nargs='*',
        default = None,
        type=str,
        help = "List of symbols to look up")

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

    test = GlobalQuote(
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
    # python -m apys.alpha_vantage.global_quote AAPL KO

    # A tidy dataframe: 1 X 10
    #     symbol      open      high       low     close    volume        date previous_close   change percent_change
    #   <object>  <object>  <object>  <object>  <object>  <object>    <object>       <object> <object>       <object>
    # 0     AAPL  186.0600  186.7400  185.1900  185.9200  40477782  2024-01-12       185.5900   0.3300        0.1778%
    # 0       KO   60.0800   60.4600   59.8700   60.3900  13218008  2024-01-12        59.8100   0.5800        0.9697%

    # ['CSCO', 'IWM', 'VIST', 'PKX', 'NVDA', 'BITF', 'ZM', 'TM', 'T', 'TS', 'AAPL', 'ORCL', 'F', 'JPM', 'FSLR', 'JMIA', 'XLE', 'MO', 'TSLA', 'QQQ', 'EFX', 'MA', 'SHEL', 'ABNB', 'NIO', 'RBLX', 'XLF', 'AXP', 'FDX', 'SNOW', 'BIDU.NASDAQ', 'QCOM', 'AGRO', 'BA', 'TRIP', 'NMR', 'KO', 'WMT', 'DEO', 'BMY', 'MSFT', 'PAAS', 'SPY', 'TXN', 'NKE', 'KMB', 'KB', 'CVX', 'RIO', 'PYPL', 'SATL', 'SBUX', 'C', 'ROST', 'ANF', 'USB', 'BB', 'UBER', 'XOM', 'MSTR.NASDAQ', 'NOK', 'SLB', 'BABA', 'META', 'NTES', 'UPST', 'MMM', 'TWLO', 'PFE', 'DE', 'BSBR', 'ETSY', 'SID', 'EBR', 'LVS', 'JNJ', 'UGP', 'WBA', 'BP', 'HMC', 'AIG', 'AVY', 'ARCO', 'RTX', 'GOOGL', 'HOG', 'AAL', 'NEM', 'HDB', 'UNH', 'GSK', 'SYY', 'CAH', 'MELI', 'HAL', 'SBS', 'TX', 'INTC', 'AVGO', 'EWZ', 'X', 'HMY', 'GLOB', 'EEM', 'ADBE', 'HSY', 'ORAN', 'NVS', 'BK', 'SQ', 'MSI', 'WB', 'CAAP', 'MU', 'EBAY', 'LLY', 'VIV', 'HD', 'ADI', 'VZ', 'FCX', 'BRFS', 'AMD', 'AZN', 'DOCU', 'DESP', 'BBD', 'AMZN', 'IP', 'GE', 'VALE', 'PEP', 'TCOM', 'DD', 'GILD', 'IFF', 'GM', 'MOS', 'NFLX', 'COIN', 'DOW', 'SE', 'TGT', 'SCCO', 'EA', 'BIOX', 'V', 'COST', 'SUZ', 'ITUB', 'LYG', 'HUT', 'IBM', 'CDE', 'AMAT', 'BRK.B', 'GS', 'AMGN', 'NG', 'DIA', 'YY', 'HPQ', 'GOLD', 'HSBC', 'ABEV', 'CAR', 'LRCX', 'WFC', 'TMO', 'SPOT', 'GPRK', 'TEF', 'BCS', 'SNAP', 'XP', 'ARKK', 'SAN', 'SHOP', 'KEP', 'CAT', 'SONY', 'NTCO', 'SPGI', 'BHP', 'AKO.B', 'GFI', 'SAP', 'NUE', 'PAC', 'PBI', 'MDT', 'HL', 'TTE', 'CRM', 'JD', 'LMT', 'PANW', 'MCD', 'PBR', 'ABBV', 'MFG', 'ING', 'TSM', 'IBN', 'SNA', 'ADP', 'GLW', 'VOD', 'TV', 'UL', 'ABT', 'HON', 'UAL', 'FMX', 'CX', 'ERIC', 'ERJ', 'AEM', 'BG', 'PG', 'UNP', 'KOF', 'OXY', 'PSX', 'INFY', 'VRSN', 'AMX', 'HWM', 'MRK', 'GGB', 'PHG', 'CL', 'PCAR', 'BIIB', 'GRMN']