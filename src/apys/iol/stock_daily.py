#!/usr/bin/env python3
"""
Author: Fernando Corrales <corrales_fernando@hotmail.com>
Purpose: Get daily stock data from IOL
"""

import argparse
import datetime as dt
import inspect
import json
import os
import sys
from dataclasses import dataclass, field
from datar import f, dplyr, tidyr, base

import pandas as pd
import requests

from ..utils.pydyverse import PrintTibble
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
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        df = pd.DataFrame(self.response.json())

        # Returning columns
        # Index(['ultimoPrecio', 'variacion', 'apertura', 'maximo', 'minimo',
        #        'fechaHora', 'tendencia', 'cierreAnterior', 'montoOperado',
        #        'volumenNominal', 'precioPromedio', 'moneda', 'precioAjuste',
        #        'interesesAbiertos', 'puntas', 'cantidadOperaciones',
        #        'descripcionTitulo', 'plazo', 'laminaMinima', 'lote'],
        #       dtype='object')        

        df = df >> \
            tidyr.separate(
                f.fechaHora, 
                into = ['fecha', None], 
                sep = 10,
                #convert = {'fecha': dt.date}
            ) >> \
            dplyr.transmute(
                fecha = f.fecha,
                #plazo = f.plazo,
                open = f.apertura,
                high = f.maximo,
                low = f.minimo,
                close = f.ultimoPrecio,
                #prev_close = f.cierreAnterior,
                vol = f.volumenNominal
                #var = f.variacion,
                #puntas = f.puntas
            )

        # Filtramos las cotizaciones intradiarias de
        # los últimos días de cotización, si es hay
        df = df >> \
            dplyr.group_by(f.fecha) >> \
            dplyr.summarise(vol = base.max_(f.vol)) >> \
            dplyr.left_join(
                df,
                by = base.c(f.fecha, f.vol)
            ) >> \
            dplyr.relocate(
                f.vol, 
                _after = dplyr.tidyselect.last_col()
            )

        # Convertimos en tipo date la columna fecha
        df['fecha'] = pd.to_datetime(
            df['fecha'], format='%Y-%m-%d'
        )

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

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
    #python -m apys.iol.stock_daily GGAL 01-10-2022 -j True