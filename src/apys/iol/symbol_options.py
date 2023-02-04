#!/usr/bin/env python3
"""
Author: Fernando Corrales <corrales_fernando@hotmail.com>
Purpose: Get symbol's options from IOL
"""

import argparse
import inspect
import json
import os
import sys
import datetime as dt
from dataclasses import dataclass, field
from datar import dplyr, f, tidyr

import pandas as pd
import requests

from ..utils.pydyverse import PrintTibble
from ..utils.sql_utils import SQLUtils
from ..models.iol_model import IOLModel
from .connect import IOL


# --------------------------------------------------
@dataclass
class SymbolOptions(SQLUtils):
    """
    Get symbol's options from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    symbol: str
    market: str = 'bCBA'
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)
    _TABLE_NAME:str = field(init=False, repr=False, default='symbol_options')
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
        URL = (
            f"api/v2/{self.market}/Titulos/{self.symbol}/"
            f"Opciones"
        )

        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame()
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        data = (self.response.json())

        # Index(['cotizacion', 'simboloSubyacente', 'fechaVencimiento', 'tipoOpcion',
        #        'simbolo', 'descripcion', 'pais', 'mercado', 'tipo', 'plazo', 'moneda'],
        #       dtype='object')

        # "simboloSubyacente": "GGAL",
        # "fechaVencimiento": "2023-02-17T00:00:00",
        # "tipoOpcion": "Call",
        # "simbolo": "GFGC170.FE",
        # "descripcion": "Call GGAL 170.00 Vencimiento: 17/02/2023",
        # "pais": "argentina",
        # "mercado": "bcba",
        # "tipo": "OPCIONES",
        # "plazo": "t1",
        # "moneda": "peso_Argentino"

        options = []
        for i in range(len(data)):
            option = data[i]['cotizacion']
            option['symbol'] = data[i]['simbolo']
            option['subyacente'] = data[i]['simboloSubyacente']
            option['type'] = data[i]['tipoOpcion']
            option['expire'] = data[i]['fechaVencimiento']
            option['desc'] = data[i]['descripcion']
            option['term'] = data[i]['plazo']
            option['currency'] = data[i]['moneda']
            option['market'] = data[i]['mercado']
            option['country'] = data[i]['pais']
            options.append(option)
        df = pd.DataFrame(options)

        # print(df.iloc[0])
        # ultimoPrecio                                            109.562
        # variacion                                                   0.0
        # apertura                                                    0.0
        # maximo                                                      0.0
        # minimo                                                      0.0
        # fechaHora                                   0001-01-01T00:00:00
        # tendencia                                                  sube
        # cierreAnterior                                              0.0
        # montoOperado                                                0.0
        # volumenNominal                                                0
        # precioPromedio                                              0.0
        # moneda                                                        0
        # precioAjuste                                                0.0
        # interesesAbiertos                                           0.0
        # puntas                                                     None
        # cantidadOperaciones                                           0
        # descripcionTitulo                                          None
        # plazo                                                      None
        # laminaMinima                                                  0
        # lote                                                          0
        # subyacente                                                 GGAL
        # type                                                       Call
        # expire                                               2022-12-16
        # desc                   Call GGAL 132.00 Vencimiento: 16/12/2022
        # Name: GFGC132.DI, dtype: object
        df = df >> \
            tidyr.separate(
                f.expire, 
                into = ['expire', None], 
                sep = 10
            ) >> \
            tidyr.separate(
                f.desc,
                into = [None, None, 'strike', None, None],
                sep = ' ',
                remove = False
            ) >> \
            dplyr.transmute(
                date_time = f.fechaHora,
                underlying = f.subyacente,
                symbol = f.symbol,
                type = f.type,
                expire = f.expire,
                strike = f.strike,
                open = f.apertura,
                high = f.maximo,
                low = f.minimo,
                close = f.ultimoPrecio,
                bid_ask = f.puntas,
                vol = f.volumenNominal,
                var = f.variacion,
                desc = f.desc,
                # term = f.term,
                # currency = f.currency,
                # market = f.market,
                # country = f.country
            )
        # Type conversion
        df = df.astype({'strike':'float'})
        df['expire'] = pd.to_datetime(
            df['expire'], format='%Y-%m-%d'
        )

        # Days to expire
        df['days_expire'] = (df['expire'] - pd.Timestamp.now()).dt.days
        df = df >>\
            dplyr.relocate(f.days_expire, _after = f.expire)

        #df = df.set_index('symbol')

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Get symbol's options from IOL",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'symbol', 
        metavar = "Symbol",
        default='',
        type=str,
        help = "Symbol or ticker")

    parser.add_argument(
        '-m', '--market', 
        metavar = "Market's name",
        default='bCBA',
        type=str,
        help = "Market's name to filter")

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

    test = SymbolOptions(
        iol = iol,
        symbol = args.symbol,
        market = args.market
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
    # python -m apys.iol.symbol_options GGAL -j True
