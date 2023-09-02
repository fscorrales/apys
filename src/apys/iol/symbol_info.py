#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get symbol info from IOL
"""

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
import requests
from datar import dplyr, f

from ..utils.pydyverse import PrintTibble
from ..utils.sql_utils import SQLUtils
from ..models.iol_model import IOLModel
from .connect import IOL


# --------------------------------------------------
@dataclass
class SymbolInfo(SQLUtils):
    """
    Get symbol info from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    symbol: str
    market: str = 'bCBA'
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)
    _TABLE_NAME:str = field(init=False, repr=False, default='symbol_info')
    _INDEX_COL:str = field(init=False, repr=False, default='symbol')
    _FILTER_COL:str = field(init=False, repr=False, default='symbol')
    _SQL_MODEL:IOLModel = field(init=False, repr=False, default=IOLModel)

    def __post_init__(self):
        self.get_data()
        self.to_dataframe()

    def get_data(self):
        """Get response from IOL"""
        self.iol.update_token()
        h = {
            "Authorization":"Bearer " + self.iol.token["access_token"]
        }
        
        URL = f"api/v2/{self.market}/Titulos/{self.symbol}" 
        
        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame()
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json(), index=[0])   
        # Index(['simbolo', 'descripcion', 'pais', 'mercado', 
        # 'tipo', 'plazo', 'moneda'], dtype='object')

        df = df >> \
            dplyr.transmute(
                symbol = f.simbolo,
                desc = f.descripcion,
                country = f.pais,
                market = f.mercado,
                type = f.tipo,
                term = f.plazo,
                currency = f.moneda
            )

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get symbol info from IOL',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'symbol', 
        metavar = 'Symbol',
        type=str,
        help = "Symbol to look up")

    parser.add_argument(
        '-u', '--username', 
        metavar = 'Username',
        default = '',
        type=str,
        help = "Username to log in IOL")

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in IOL")

    parser.add_argument(
        '-m', '--market', 
        metavar = 'Market',
        default = 'bCBA',
        type=str,
        help = "Market to look in")

    parser.add_argument(
        '-j', '--json_file', 
        metavar = 'json file',
        default = False,
        type=bool,
        help = 'Should json file be created ' + 
        'or updated with credentials')

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    json_path = dir_path + '/iol.json'
    if args.username != '' and args.password != '':
        iol = IOL(args.username, args.password)
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                iol = IOL(
                    data_json['username'],
                    data_json['password'],
                    access_token= data_json['access_token'],
                    datetime_expires= data_json['expires']
                )
            json_file.close()
        else:
            msg = (
                f'If {json_path} with username and password ' +
                'as keys does not exist in the directory, ' + 
                'both arguments must be given.'
            )
            sys.exit(msg)

    test = SymbolInfo(
        iol = iol,
        symbol = args.symbol,
        market = args.market,
    )
    test.print_tibble()
    test.to_sql(dir_path + '/iol.sqlite')

    # json_file created with credentials
    if args.json_file:
        data_json = {
            "username": iol._username,
            "password": iol._password,
            "access_token": iol.token['access_token'],
            "expires": iol.token['.expires']
        }
        with open(json_path, 'w') as json_file:
            json.dump(data_json, json_file)
        json_file.close()

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.iol.symbol_info GGAL -j True

    # A tidy dataframe: 1 X 7
    #     symbol                          desc    country   market      type     term        currency
    #   <object>                      <object>   <object> <object>  <object> <object>        <object>
    # 0     GGAL  Grupo Financiero Galicia S.A  argentina     bcba  ACCIONES       t2  peso_Argentino