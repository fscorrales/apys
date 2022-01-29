# %%
import json
import requests

from Exceptions import APIException
from Exceptions import APIRequestException


class Finnhub:
    data = None
    API_URL = "https://finnhub.io/api/v1"
    DEFAULT_TIMEOUT = 10

    def __init__(self, api_key, proxies = None):
        self._session = self._init_session(api_key, proxies)

    @staticmethod
    def _init_session(api_key, proxies):
        session = requests.session()
        session.params["token"] = api_key
        if proxies is not None:
            session.proxies.update(proxies)
        return session

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _request(self, method, path, subset, **kwargs):
        uri = "{}/{}".format(self.API_URL, path)
        kwargs["timeout"] = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        kwargs["params"] = self._format_params(kwargs.get("params", {}))

        response = getattr(self._session, method)(uri, **kwargs)
        return self._handle_response(response, subset)
        #return response.json()[subset]

    def _handle_response(self, response, subset):
        if not response.ok:
            raise APIException(response)
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                if subset != None:
                    self.data = response.json()[subset]
                else:
                    self.data = response.json()
                return self.data
            if 'text/csv' in content_type:
                return response.text
            if 'text/plain' in content_type:
                return response.text
            raise APIRequestException("Invalid Response: {}".format(response.text))
        except ValueError:
            raise APIRequestException("Invalid Response: {}".format(response.text))
    '''
    @staticmethod
    def _merge_two_dicts(first, second):
        result = first.copy()
        result.update(second)
        return result
    '''

    @staticmethod
    def _format_params(params):
        return {k: json.dumps(v) if isinstance(v, bool) else v for k, v in params.items()}
    
    def _get(self, path, subset, **kwargs):
        return self._request("get", path, subset, **kwargs)

    @property
    def api_key(self):
        return self._session.params.get("token")

    @api_key.setter
    def api_key(self, api_key):
        self._session.params["token"] = api_key

    #STOCK FUNDAMENTALS
    def symbol_lookup(self, query):
        params = {"q": query}
        subset = "result"
        return self._get("/search", subset = subset, params=params)

    def crypto_exchanges(self):
        params = {}
        subset = None
        return self._get("/crypto/exchange", subset = subset, params=params)