#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get available instruments by country from IOL
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
from .connect import IOL
from ..models.iol_model import IOLModel

# --------------------------------------------------
@dataclass
class AssetClassCountry(SQLUtils):
    """
    Get available instruments by country from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    country: str #argentina o estados_Unidos
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)
    _TABLE_NAME:str = field(init=False, repr=False, default='asset_class_country')
    _INDEX_COL:str = field(init=False, repr=False, default='')
    _FILTER_COL:str = field(init=False, repr=False, default='country')
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
        URL = (
            f"api/v2/{self.country}/Titulos/Cotizacion/Instrumentos"
        )

        self.response = self.iol.get(URL, headers = h)
        self.to_dataframe()

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json())
        # Index(['instrumento', 'pais'], dtype='object')

        df = df >> \
            dplyr.transmute(
                asset_class = f.instrumento,
                country = f.pais
            )

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get available instruments by country from IOL',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'country', 
        metavar = "Country's name",
        default='',
        type=str,
        help = "Country's name to filter")

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

    # sql_path = dir_path + '/iol.sqlite'
    # with ConnectDB(sql_path) as con:
    #     test = InstrumentsCountry(
    #         iol = iol,
    #         country = args.country,
    #         engine = con.engine
    #     )
    #     test.print_tibble()

    test = AssetClassCountry(
        iol = iol,
        country = args.country
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
    # python -m apys.iol.asset_class_country argentina -j True
    
    # A tidy dataframe: 6 X 2
    #   asset_class   country
    #     <object>   <object>
    # 0   Acciones  argentina
    # 1      Bonos  argentina
    # 2   Opciones  argentina
    # 3  Cauciones  argentina
    # 4    Futuros  argentina
    # 5        FCI  argentina