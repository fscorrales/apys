#!/usr/bin/env python3
"""
Author: Fernando Corrales <corrales_fernando@hotmail.com>
Purpose: Get daily stock data from IOL
"""

import argparse
import datetime as dt
import json
import inspect
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
import requests

from ..utils.validation import valid_date
from .connect import IOL


# --------------------------------------------------
@dataclass
class StockDaily:
    """
    Get daily stock data from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    symbol: str
    from_date: dt.date
    to_date: dt.date = dt.date.today()
    market: str = 'bCBA'
    adjusted: bool = False
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.get_data()
        self.to_dataframe()

    def get_data(self):
        """Get response from IOL"""
        self.iol.update_token()
        h = {
            "Authorization":"Bearer " + self.iol.token["access_token"]
        }

        from_date = dt.datetime.strftime(self.from_date, "%Y-%m-%d")
        to_date = dt.datetime.strftime(self.to_date, "%Y-%m-%d")

        if self.adjusted == True:
            adjusted = "ajustada"
        else:
            adjusted = "sinAjustar"
        
        URL = (
            f"api/v2/{self.market}/Titulos/{self.symbol}" 
            f"/Cotizacion/seriehistorica/{from_date}/{to_date}/{adjusted}"
        )
        

        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame() 

    def to_dataframe(self):
        """Transform response to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json())
            
        df.columns = ["close", "var", "open", "high", "low", "fecha_hora",
        "tendencia", "previous_close", "monto_operado", "volumen_nominal",
        "precio_promedio", "moneda", "precio_ajuste", "open_interest",
        "puntas", "q_operaciones", "descripcion", "plazo", "min_lamina", "lote"]
            
        self.df = df

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get daily stock data from IOL',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'symbol', 
        metavar = 'Symbol',
        type=str,
        help = "Symbol to look up")

    parser.add_argument(
        'from_date', 
        metavar = 'from_date',
        type=valid_date,
        help = "The Start Date - format DD-MM-YYYY")

    parser.add_argument(
        '-to', '--to_date', 
        metavar = 'to_date',
        default = dt.datetime.strftime(dt.date.today(), "%d-%m-%Y"),
        type=valid_date,
        help = "The End Date - format DD-MM-YYYY")

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
        '-a', '--adjusted', 
        metavar = 'Price adjustement',
        default = False,
        type=bool,
        help = "Should price be adjusted")

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

    test = StockDaily(
        iol = iol,
        symbol = args.symbol,
        from_date = args.from_date,
        to_date = args.to_date,
        market = args.market,
        adjusted = args.adjusted
    )

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

    print(test.df.head(5))

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    #python -m apys.iol.stock_daily GGAL 01-10-2022