#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Purpose: Get symbol's last price from IOL
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
from ..utils.sql_utils import SQLUtils
from ..models.iol_model import IOLModel
from .connect import IOL


# --------------------------------------------------
@dataclass
class SymbolLastPrice(SQLUtils):
    """
    Get symbol's last price from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    symbol: str
    market: str = 'bCBA'
    response: requests.Response = field(init=False, repr=False)
    df: pd.DataFrame = field(init=False, repr=False)
    _TABLE_NAME:str = field(init=False, repr=False, default='symbol_last_price')
    _INDEX_COL:str = field(init=False, repr=False, default='id')
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
            f"CotizacionDetalleMobile"
        )

        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame()
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json())

        # Index(['operableCompra', 'operableVenta', 'visible', 'ultimoPrecio',
        #        'variacion', 'apertura', 'maximo', 'minimo', 'fechaHora', 'tendencia',
        #        'cierreAnterior', 'montoOperado', 'volumenNominal', 'precioPromedio',
        #        'moneda', 'precioAjuste', 'interesesAbiertos', 'puntas',
        #        'cantidadOperaciones', 'simbolo', 'pais', 'mercado', 'tipo',
        #        'descripcionTitulo', 'plazo', 'laminaMinima', 'lote', 'cantidadMinima',
        #        'puntosVariacion'],
        #       dtype='object')

        # Puntas =
        # {'cantidadCompra': 3.0, 'precioCompra': 152.5, 
        # 'precioVenta': 152.75, 'cantidadVenta': 5545.0}

        df = pd.concat([df, df['puntas'].apply(pd.Series)], axis=1)
        df = df >> \
            tidyr.separate(
                f.fechaHora, 
                into = ['date_time', None], 
                sep = 19
            ) >> \
            dplyr.transmute(
                symbol = f.simbolo,
                type = f.tipo,
                date_time = f.date_time,
                open = f.apertura,
                high = f.maximo,
                low = f.minimo,
                close = f.ultimoPrecio,
                bid_q = f.cantidadCompra,
                bid_price = f.precioCompra,
                ask_price = f.precioVenta,
                ask_q = f.cantidadVenta,
                vol = f.volumenNominal,
                desc = f.descripcionTitulo,
                market = f.mercado,
                currency = f.moneda,
                country = f.pais,
                term = f.plazo,
                lote = f.lote,
                lamina_min = f.laminaMinima,
                q_min = f.cantidadMinima,
                shown = f.visible,
                buyable = f.operableCompra,
                sellable = f.operableVenta
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
        description = "Get symbol's last price from IOL",
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

    test = SymbolLastPrice(
        iol = iol,
        symbol= args.symbol,
        market=args.market
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
    # python -m apys.iol.symbol_last_price GGAL -j True

    # A tidy dataframe: 5 X 23
    #     symbol      type           date_time      open      high       low     close     bid_q  bid_price  ask_price     ask_q      vol                          desc  ...
    #   <object>  <object>    <datetime64[ns]> <float64> <float64> <float64> <float64> <float64>  <float64>  <float64> <float64>  <int64>                      <object>  ...
    # 0     GGAL  acciones 2022-11-28 18:00:01     253.0    253.85     249.0     253.6      50.0      250.0      255.0     159.0  1111957  Grupo Financiero Galicia S.A  ...
    # 1     GGAL  acciones 2022-11-28 18:00:01     253.0    253.85     249.0     253.6     132.0      242.5      256.0     906.0  1111957  Grupo Financiero Galicia S.A  ...
    # 2     GGAL  acciones 2022-11-28 18:00:01     253.0    253.85     249.0     253.6      10.0      236.0      258.0      20.0  1111957  Grupo Financiero Galicia S.A  ...
    # 3     GGAL  acciones 2022-11-28 18:00:01     253.0    253.85     249.0     253.6      50.0      235.5      259.0    2000.0  1111957  Grupo Financiero Galicia S.A  ...
    # 4     GGAL  acciones 2022-11-28 18:00:01     253.0    253.85     249.0     253.6    6679.0      225.0      260.0    2278.0  1111957  Grupo Financiero Galicia S.A     
    #... with 10 more columns: market <object>, currency <object>, country <object>, term <object>, lote <int64>, lamina_min <int64>, q_min <int64>, shown <bool>, buyable <bool>, sellable <bool>