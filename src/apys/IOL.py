import json
import requests
import pandas as pd
import datetime as dt

from Exceptions import APIException
from Exceptions import APIRequestException

#API DOC: https://api.invertironline.com/

class IOL:
    data = None
    API_URL = "https://api.invertironline.com"
    DEFAULT_TIMEOUT = 10
    _username = None
    _password = None
    token = None

    def __init__(self, iol_username, iol_password):
        self._username = iol_username
        self._password = iol_password
        self.token()

    def token(self):
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
            self.token = self.token()
            return (f"Token has been updated. Expires in {self.token['.expires']}")

    def _request(self, method, path, headers, **kwargs):
        uri = "{}/{}".format(self.API_URL, path)
        kwargs["headers"] = headers
        kwargs["timeout"] = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        kwargs["params"] = self._format_params(kwargs.get("params", {}))

        response = getattr(requests, method)(uri, **kwargs)
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
    
    def _get(self, path = None, headers = None,**kwargs):
        return self._request("get", path, headers, **kwargs)

    @property
    def api_key(self):
        return self._session.params.get("token")

    @api_key.setter
    def api_key(self, api_key):
        self._session.params["token"] = api_key

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", **params):
        return self._get(endpoint, params=params)

    def stock_daily(self, symbol, market = "bCBA", 
    from_date = "2010-01-01", to_date = "",
    adjusted = False, output_df = True):
        self.update_token()
        h = {
            "Authorization":"Bearer " + self.token["access_token"]
        }

        if adjusted == True:
            adjusted = "ajustada"
        else:
            adjusted = "sinAjustar"

        if (to_date == ""):
            to_date = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")
        
        URL = f"api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{from_date}/{to_date}/{adjusted}"
        data = self._get(URL, headers = h)
        if output_df == True:
            df = pd.DataFrame(data)
                
            df.columns = ["close", "var", "open", "high", "low", "fecha_hora",
            "tendencia", "previous_close", "monto_operado", "volumen_nominal",
            "precio_promedio", "moneda", "precio_ajuste", "open_interest",
            "puntas", "q_operaciones", "descripcion", "plazo", "min_lamina", "lote"]
                
            self.data = df
        else:
            self.data = data
        return self.data
