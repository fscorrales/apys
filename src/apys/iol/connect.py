import datetime as dt
from dataclasses import dataclass, field

import requests

from ..general_requests import APIRequests

#API DOC: https://api.invertironline.com/

@dataclass
class IOL(APIRequests):
    _username: str = ''
    _password: str = ''
    access_token: str = ''
    datetime_expires: str = ''
    token: dict = field(
        default_factory=dict, 
        init=False, repr=False)
    API_URL: str = field(
        default="https://api.invertironline.com", 
        init=False, repr=False)
    DEFAULT_TIMEOUT: int = field(
        default=10, 
        init=False, repr=False)

    def __post_init__(self):
        if self.access_token == '' or self.datetime_expires == '':
            self.get_token()
        else:
            self.token['access_token'] = self.access_token
            self.token['.expires'] = self.datetime_expires       

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

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", **params):
        return self.get(endpoint, params=params)