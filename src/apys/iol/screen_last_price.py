#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get screen's last price from IOL
"""

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
import requests
from datar import dplyr, f, tidyr

from ..models.iol_model import IOLModel
from ..utils.pydyverse import PrintTibble
from ..utils.sql_utils import SQLUtils
from .connect import IOL


# --------------------------------------------------
@dataclass
class ScreenLastPrice(SQLUtils):
    """
    Get screen's last price from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    instrument: str = 'Acciones'
    screen: str = 'Merval'
    country: str = 'argentina'
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)
    _TABLE_NAME:str = field(init=False, repr=False, default='screen_last_price')
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
            f"api/v2/Cotizaciones/{self.instrument}/"
            f"{self.screen}/{self.country}"
        )

        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame()
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json()['titulos'])
        # Index(['simbolo', 'descripcion', 'puntas', 'ultimoPrecio',
        #        'variacionPorcentual', 'apertura', 'maximo', 'minimo', 'ultimoCierre',
        #        'volumen', 'cantidadOperaciones', 'fecha', 'tipoOpcion',
        #        'precioEjercicio', 'fechaVencimiento', 'mercado', 'moneda'],
        #         dtype='object')

        # Puntas =
        # {'cantidadCompra': 3.0, 'precioCompra': 152.5, 
        # 'precioVenta': 152.75, 'cantidadVenta': 5545.0}

        df['date_time'] = df['fecha'].str[0:19]
        df['country'] = self.country
        df['asset_class'] = self.instrument
        df['screen'] = self.screen
        if isinstance(type(df['puntas'][0]), dict):
            df = pd.concat([df, df['puntas'].apply(pd.Series)], axis=1)
        else:
            df['cantidadCompra'] = 0
            df['precioCompra'] = 0
            df['precioVenta'] = 0
            df['cantidadVenta'] = 0
        df.drop(
            columns=[
                'variacionPorcentual', 'ultimoCierre', 'cantidadOperaciones',
                'fecha', 'tipoOpcion', 'precioEjercicio', 'fechaVencimiento',
                'mercado', 'moneda', 'puntas'
            ], inplace=True
        )
        df.rename(columns={
            'simbolo':'symbol',
            'descripcion':'desc',
            'apertura':'open',
            'maximo':'high',
            'minimo':'low',
            'ultimoPrecio':'close',
            'cantidadCompra':'bid_q',
            'precioCompra':'bid_price',
            'precioVenta':'ask_price',
            'cantidadVenta':'ask_q',
            'volumen':'vol',
        }, inplace=True, copy=False)

        # Convertimos en tipo date la columna fecha
        df['date_time'] = pd.to_datetime(
            df['date_time'], format='%Y-%m-%dT%H:%M:%S'
        )

        # Drop duplicated rows by symbol if any
        df = df.drop_duplicates(subset=['symbol'])

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = "Get screen's last price from IOL",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-i', '--instrument', 
        metavar = "Instrument's type",
        default='Acciones',
        type=str,
        help = "Instrument's type to filter")

    parser.add_argument(
        '-s', '--screen', 
        metavar = "Screen's name",
        default='Merval',
        type=str,
        help = "Screen's name to filter")

    parser.add_argument(
        '-c', '--country', 
        metavar = "Country's name",
        default='argentina',
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

    print(args.instrument)
    print(args.screen)

    test = ScreenLastPrice(
        iol = iol,
        instrument= args.instrument,
        screen=args.screen,
        country = args.country
    )
    # df = test.df
    # symbol = df['symbol']
    # print(df[symbol.isin(symbol[symbol.duplicated()])])
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
    # python -m apys.iol.screen_last_price -i Acciones -s "Merval Argentina" -j True

    # A tidy dataframe: 3221 X 12
    #        symbol     desc               date_time      open      high       low     close     bid_q  bid_price  ask_price     ask_q  ...
    #      <object> <object>        <datetime64[ns]> <float64> <float64> <float64> <float64> <float64>  <float64>  <float64> <float64>  ...
    # 0  ALUC100.AB     None 2022-11-25 03:00:08.720     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 1  ALUC100.EN     None 2022-11-25 03:00:18.870     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 2  ALUC10072D     None 2022-11-25 03:00:12.313     0.000     0.000     0.000     0.000      17.0       57.5     59.433      10.0  ...
    # 3  ALUC10072F     None 2022-11-25 03:00:18.230     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 4  ALUC105.AB     None 2022-11-25 03:00:18.230     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 5  ALUC105.EN     None 2022-11-25 03:00:24.707     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 6  ALUC110.AB     None 2022-11-25 03:00:22.023     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 7  ALUC110.DI     None 2022-11-25 03:00:28.550    42.551    42.551    42.551    42.551       0.0        0.0     50.664      10.0  ...
    # 8  ALUC110.EN     None 2022-11-25 03:00:15.430     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0  ...
    # 9  ALUC110.FE     None 2022-11-25 03:00:17.717     0.000     0.000     0.000     0.000       0.0        0.0      0.000       0.0     
    #... with 3211 more rows, and 1 more columns: vol <float64>