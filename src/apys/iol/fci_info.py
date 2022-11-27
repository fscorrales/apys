#!/usr/bin/env python3
"""
Author: Fernando Corrales <corrales_fernando@hotmail.com>
Purpose: Get FCI symbol data from IOL
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
from .connect import IOL


# --------------------------------------------------
@dataclass
class FCIInfo:
    """
    Get fci info from IOL
    :param IOL must be initialized first
    """
    iol: IOL
    symbol: str = ''
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
        URL = (
            f"api/v2/Titulos/FCI"
        )
        if self.symbol != '':
            URL = URL + f'/{self.symbol}'

        self.response = self.iol.get(URL, headers = h)
        # As precaution if someone wants to use this method
        # without transforming response to DataFrame
        self.df = pd.DataFrame()
        return self.response 

    def to_dataframe(self):
        """Transform to Pandas DataFrame"""
        if self.symbol == '':
            df = pd.DataFrame(self.response.json())
        else:
            df = pd.DataFrame(self.response.json(), index=[0])
        
        # Index(['variacion', 'ultimoOperado', 'horizonteInversion', 'rescate',
        # 'invierte', 'tipoFondo', 'avisoHorarioEjecucion',
        # 'tipoAdministradoraTituloFCI', 'fechaCorte', 'codigoBloomberg',
        # 'perfilInversor', 'informeMensual', 'reglamentoGestion',
        # 'variacionMensual', 'variacionAnual', 'simbolo', 'descripcion', 'pais',
        # 'mercado', 'tipo', 'plazo', 'moneda'], dtype='object')

        df = df >> \
            dplyr.transmute(
                symbol = f.simbolo,
                desc = f.descripcion,
                type = f.tipoFondo,
                adm_type = f.tipoAdministradoraTituloFCI,
                horizon = f.horizonteInversion,
                profile = f.perfilInversor,
                yearly_var = f.variacionAnual,
                monthly_var = f.variacionMensual,
                investment = f.invierte,
                term = f.plazo,
                rescue = f.rescate,
                report = f.informeMensual,
                regulation = f.reglamentoGestion,
                currency = f.moneda,
                country = f.pais,
                market = f.mercado,
                bloomberg = f.codigoBloomberg
            )

        self.df = (df) 
        return self.df

    def print_tibble(self):
        print(PrintTibble(self.df))

# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Get FCI info from IOL',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--symbol', 
        metavar = "FCI's name",
        default='',
        type=str,
        help = "FCI's name to filter")

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

    test = FCIInfo(
        iol = iol,
        symbol = args.symbol,
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
    # python -m apys.iol.fci_info -j True