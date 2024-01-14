#!/usr/bin/env python3
"""
Author: Fernando Corrales <fscpython@gmail.com>
Source: 
API Doc: https://www.alphavantage.co/documentation/
Purpose: Log to AlphaVantage
Require package: 
    -   pip install ...
"""

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass, field

import requests

from ..general_requests import APIRequests


# --------------------------------------------------
@dataclass
class AlphaVantage(APIRequests):
    data = None
    API_URL = "https://www.alphavantage.co/query"
    DEFAULT_TIMEOUT = 10

    def __init__(self, api_key, proxies = None):
        self._session = self._init_session(api_key, proxies)

    @staticmethod
    def _init_session(api_key, proxies):
        session = requests.session()
        session.params["apikey"] = api_key
        if proxies is not None:
            session.proxies.update(proxies)
        return session

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _request(self, method, path, **kwargs):
        uri = "{}/{}".format(self.API_URL, path)
        kwargs["timeout"] = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        kwargs["params"] = self._format_params(kwargs.get("params", {}))

        response = getattr(self._session, method)(uri, **kwargs)
        return self._handle_response(response)
        #return response.json()[subset]

    def _handle_response(self, response):
        if not response.ok:
            raise APIException(response)
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return response.json()
            if 'text/csv' in content_type:
                return response.text
            if 'text/plain' in content_type:
                return response.text
            raise APIRequestException("Invalid Response: {}".format(response.text))
        except ValueError:
            raise APIRequestException("Invalid Response: {}".format(response.text))

    @staticmethod
    def _format_params(params):
        return {k: json.dumps(v) if isinstance(v, bool) else v for k, v in params.items()}
    
    def _get(self, path, **kwargs):
        return self._request("get", path, **kwargs)

    @property
    def api_key(self):
        return self._session.params.get("apikey")

    @api_key.setter
    def api_key(self, api_key):
        self._session.params["apikey"] = api_key

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", **params):
        return self._get(endpoint, params=params)

# --------------------------------------------------
class APIException(Exception):
    def __init__(self, response):
        super(APIException, self).__init__()

        self.code = 0
    
        try:
            json_response = response.json()
        except ValueError:
            self.message = "JSON error message: {}".format(response.text)
        else:
            if "error" not in json_response:
                self.message = "Wrong json format from API"
            else:
                self.message = json_response["error"]

        self.status_code = response.status_code
        self.response = response

    def __str__(self):
        return "APIException(status_code: {}): {}".format(self.status_code, self.message)

# --------------------------------------------------
class APIRequestException(Exception):
    def __init__(self, message):
        super(APIRequestException, self).__init__()
        self.message = message

    def __str__(self):
        return "APIRequestException: {}".format(self.message)
    
# --------------------------------------------------
def get_args():
    """Get needed params from user input"""
    parser = argparse.ArgumentParser(
        description = 'Log to Alpha Vantage',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-p', '--password', 
        metavar = 'Password',
        default = '',
        type=str,
        help = "Password to log in API Alpha Vantage")
    
    # parser.add_argument(
    #     '-a', '--account', 
    #     metavar = 'account',
    #     default = '',
    #     type=str,
    #     help = "Account to log in pyRofex")
    
    # parser.add_argument('--live', action='store_true')
    # parser.add_argument('--no-live', dest='live', action='store_false')
    # parser.set_defaults(live=False)

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Let's try it"""
    args = get_args()
    dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    json_path = dir_path + '/credentials.json'

    
    if args.password != '':
        pr = AlphaVantage(
            api_key = args.password
        )
    else:
        if os.path.isfile(json_path):
            with open(json_path) as json_file:
                data_json = json.load(json_file)
                pr = AlphaVantage(
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

# --------------------------------------------------
if __name__ == '__main__':
    main()
    # From apys.src
    # python -m apys.alpha_vantage.alpha_vantage_login