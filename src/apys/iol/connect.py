import json
import requests
import pandas as pd
import datetime as dt

#API DOC: https://api.invertironline.com/

class IOL:
    API_URL = "https://api.invertironline.com"
    DEFAULT_TIMEOUT = 10
    _username = None
    _password = None
    token = {}

    def __init__(self, iol_username, iol_password,
    token = '', token_expires = ''):
        self._username = iol_username
        self._password = iol_password
        if token == '' or token_expires == '':
            self.get_token()
        else:
            self.token['access_token'] = token
            self.token['.expires'] = token_expires

    def get_token(self):
        url = self.API_URL + "/token"
        h = {"Content-Type":"application/x-www-form-urlencoded"}
        body = {
            "username":self._username,
            "password":self._password,
            "grant_type":"password"
        }
        r = requests.post(url, headers = h, 
        data = body)
        if r.status_code == 200:
            self.token = (r.json())
            return (f"El access token expira el {self.token['.expires']}")
        else:
            return (f"Error: {r.status_code} con respuesta = {r.text}")

    def update_token(self):
        #Time to expire
        expire = dt.datetime.strptime(self.token['.expires'],
        '%a, %d %b %Y %H:%M:%S GMT')
        now = dt.datetime.utcnow()
        diff_time = expire - now
        days = diff_time.days

        if days == 0:
            return self.token
        else:
            self.token = self.get_token()
            return (f"Token has been updated. Expires in {self.token['.expires']}")

    def _request(self, method, path, headers, **kwargs):
        uri = "{}/{}".format(self.API_URL, path)
        kwargs["headers"] = headers
        kwargs["timeout"] = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        kwargs["params"] = self._format_params(kwargs.get("params", {}))

        response = getattr(requests, method)(uri, **kwargs)
        return self._handle_response(response)
        #return response.json()[subset]

    # def _handle_response(self, response):
    #     if not response.ok:
    #         raise APIException(response)
    #     try:
    #         content_type = response.headers.get('Content-Type', '')
    #         if 'application/json' in content_type:
    #             return response.json()
    #         if 'text/csv' in content_type:
    #             return response.text
    #         if 'text/plain' in content_type:
    #             return response.text
    #         raise APIRequestException("Invalid Response: {}".format(response.text))
    #     except ValueError:
    #         raise APIRequestException("Invalid Response: {}".format(response.text))

    # @staticmethod
    # def _format_params(params):
    #     return {k: json.dumps(v) if isinstance(v, bool) else v for k, v in params.items()}
    
    # def _get(self, path = None, headers = None,**kwargs):
    #     return self._request("get", path, headers, **kwargs)

    # @property
    # def api_key(self):
    #     return self._session.params.get("token")

    # @api_key.setter
    # def api_key(self, api_key):
    #     self._session.params["token"] = api_key

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", **params):
        return self._get(endpoint, params=params)