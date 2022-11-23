import json

import requests
from .Exceptions import APIException


class APIRequests:
    def request(self, method, path, headers, **kwargs):
        uri = "{}/{}".format(self.API_URL, path)
        kwargs["headers"] = headers
        kwargs["timeout"] = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        kwargs["params"] = self.format_params(kwargs.get("params", {}))

        response = getattr(requests, method)(uri, **kwargs)
        return self.handle_response(response)

    def handle_response(self, response):
        if not response.ok:
            raise APIException(response)
        else:
            return response
        # try:
        #     content_type = response.headers.get('Content-Type', '')
        #     if 'application/json' in content_type:
        #         return response.json()
        #     if 'text/csv' in content_type:
        #         return response.text
        #     if 'text/plain' in content_type:
        #         return response.text
        #     raise APIRequestException("Invalid Response: {}".format(response.text))
        # except ValueError:
        #     raise APIRequestException("Invalid Response: {}".format(response.text))

    @staticmethod
    def format_params(params):
        return {k: json.dumps(v) if isinstance(v, bool) else v for k, v in params.items()}
    
    def get(self, path = None, headers = None,**kwargs):
        return self.request("get", path, headers, **kwargs)

    # @property
    # def api_key(self):
    #     return self._session.params.get("token")

    # @api_key.setter
    # def api_key(self, api_key):
    #     self._session.params["token"] = api_key