#!/usr/bin/env python3
"""
Author: Fernando Corrales <corrales_fernando@hotmail.com>
Purpose: Get screen options's last price from IOL
"""

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass, field
from datar import dplyr, f, tidyr

import pandas as pd
import requests

from ..utils.pydyverse import PrintTibble
from .connect import IOL
from .screen_last_price import ScreenLastPrice
from .symbol_options import SymbolOptions


# --------------------------------------------------
@dataclass
class StockOptions:
    """
    Get screen's last price from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    screen: str = 'Merval'
    country: str = 'argentina'
    screen_options = ScreenLastPrice = field(init=False, repr=False)
    screen_instrument = ScreenLastPrice = field(init=False, repr=False)
    symbol_options = SymbolOptions = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.screen_instrument = ScreenLastPrice(self.iol, 
        instrument='Acciones', screen=self.screen, country=self.country)
        self.screen_options = ScreenLastPrice(self.iol, 
        instrument='Opciones', screen='De Acciones', country=self.country)
        self.join_data()

    def join_data(self):
        pass

    def transform_data(self):
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

        df = pd.concat([df, df['puntas'].apply(pd.Series)], axis=1)
        df = df >> \
            tidyr.separate(
                f.fecha, 
                into = ['date_time', None], 
                sep = 19
            ) >> \
            dplyr.transmute(
                symbol = f.simbolo,
                # option_type = f.tipoOpcion,
                # exercise_price = f.precioEjercicio,
                # expire = f.fechaVencimiento,
                desc = f.descripcion,
                date_time = f.date_time,
                open = f.apertura,
                high = f.maximo,
                low = f.minimo,
                close = f.ultimoPrecio,
                bid_q = f.cantidadCompra,
                bid_price = f.precioCompra,
                ask_price = f.precioVenta,
                ask_q = f.cantidadVenta,
                vol = f.volumen
            )

        # Convertimos en tipo date la columna fecha
        df['date_time'] = pd.to_datetime(
            df['date_time'], format='%Y-%m-%dT%H:%M:%S'
        )

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

    test = StockOptions(
        iol = iol,
        instrument= args.instrument,
        screen=args.screen,
        country = args.country
    )
    test.print_tibble()

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
    # python -m apys.iol.screen_last_price -i Opciones -s "De Acciones" -j True

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