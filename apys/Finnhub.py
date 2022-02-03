# %%
import json
import requests
import pandas as pd
from datetime import datetime as dt

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
    
    def _get(self, path, subset = None, **kwargs):
        return self._request("get", path, subset, **kwargs)

    @property
    def api_key(self):
        return self._session.params.get("token")

    @api_key.setter
    def api_key(self, api_key):
        self._session.params["token"] = api_key

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", 
    subset = None, **params):
        return self._get(endpoint, subset = subset, params=params)

    #STOCK FUNDAMENTALS
    def symbol_lookup(self, query, 
    subset = "result"):
        params = {"q": query}
        return self._get("/search", subset = subset, params=params)

    def stock_symbols(self, exchange, **kwargs):
        params = {"exchange": exchange, **kwargs}
        return self._get("/stock/symbol", params=params)

    def company_profile(self, subset = None, **params):
        #Premium access required
        return self._get("/stock/profile", subset = subset, params=params)

    def company_profile2(self, subset = None, **params):
        return self._get("/stock/profile2", subset = subset, params=params)

    def market_news(self, category = "crypto", **kwargs):
        #category = This parameter can be 1 of the following 
        #values general, forex, crypto, merger.
        params = {"category": category, **kwargs}
        return self._get("/news", params=params)

    def company_news(self, symbol, from_date,
    to_date):
        params = {"symbol":symbol, 
                "from":from_date, "to":to_date}
        return self._get("/company-news", params=params)

    def peers(self, symbol):
        params = {"symbol": symbol}
        return self._get("/stock/peers", params=params)

    def stock_basic_financials(self, symbol, 
    metric = "all", subset = None):
        params = {"symbol":symbol, "metric":metric}
        return self._get("/stock/metric", subset = subset, params=params)

    def stock_insider_transactions(self, symbol, 
    from_date=None, to_date=None, subset = "data"):
        params = {"symbol":symbol, 
                "from":from_date, "to":to_date}
        return self._get("/stock/insider-transactions", 
        subset = subset, params=params)

    def financials_reported(self, subset = "data", **params):
        return self._get("/stock/financials-reported",
        subset = subset, params=params)

    def sec_filings(self, **params):
        return self._get("/stock/filings", params=params)

    def ipo_calendar(self, from_date, to_date, 
    subset = "ipoCalendar"):
        params = {"from":from_date, "to":to_date}
        return self._get("/calendar/ipo", 
        subset = subset, params=params)

    #STOCK ESTIMATES
    def recommendation_trends(self, symbol):
        params = {"symbol":symbol}
        return self._get("/stock/recommendation", params=params)

    def recomendation_rank(self, symbol):
        data = self.recommendation_trends(symbol)
        df = pd.DataFrame(data)
        df['period'] = pd.to_datetime(df.period)
        df.set_index('period', inplace=True)
        df.drop(['symbol'], axis=1, inplace=True)
        weights = [2, 1, -1, 3, -2]
        points = df.mul(weights, axis=1).sum(axis=1)
        n = df.sum(axis=1)
        mean_points = points / n
        summary = pd.concat([points, n, mean_points], axis=1)
        summary.columns = ['points', 'n', 'mean_points']
        summary = summary.sort_values('period', ascending=True)
        init = float(summary[0:1]['mean_points'])
        summary["idx100"] = 100 * summary['mean_points']/init
        self.data = summary
        return self.data

    def eps_surprises(self, symbol, limit=None):
        params = {"symbol": symbol, "limit": limit}
        return self._get("/stock/earnings", params=params)

    def earnings_calendar(self, 
    subset = "earningsCalendar",**params):
        return self._get("/calendar/earnings", 
        subset = subset, params=params)

    #STOCK PRICE
    def stock_quote(self, symbol):
        params = {"symbol":symbol}
        return self._get("/quote", params=params)

    def stock_candles(self, symbol, from_date, to_date, 
    resolution = "D", adj = True, subset = None):
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date),
                "adjusted":adj}
        return self._get("/stock/candle", 
        subset = subset, params=params)

    #ETFS & INDICES
    def indices_constituents(self, symbol, 
    subset = "constituents"):
        params = {"symbol":symbol}
        return self._get("/index/constituents", 
        subset = subset, params=params)


    #FOREX
    def forex_exchanges(self):
        params = {}
        return self._get("/forex/exchange", params=params)

    def forex_symbols(self, exchange):
        params = {"exchange":exchange}
        return self._get("/forex/symbol", params=params)

    #CRYPTO
    def crypto_exchanges(self):
        params = {}
        return self._get("/crypto/exchange", params=params)

    def crypto_symbols(self, exchange):
        params = {"exchange":exchange}
        return self._get("/crypto/symbol", params=params)

    def crypto_candles(self, symbol, from_date, to_date, 
    resolution = "D", subset = None):
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date)}
        return self._get("/crypto/candle", 
        subset = subset, params=params)

    #TECHNICAL ANALYSIS
    def technical_indicator(self, symbol, from_date, to_date, 
    indicator, resolution = "D", subset = None, **indicator_fields):
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date),
                "indicator":indicator, **indicator_fields}
        return self._get("/indicator", 
        subset = subset, params=params)

    #ALTERNATIVE DATA
    def stock_social_sentiment(self, symbol, 
    from_date=None, to_date=None, subset = None):
        params = {"symbol":symbol, "from":from_date, 
                "to":to_date}
        return self._get("/stock/social-sentiment", 
        subset = subset, params=params)

    def stock_uspto_patents(self, symbol, from_date, 
    to_date, subset = "data"):
        params = {"symbol":symbol, "from":from_date, 
                "to":to_date}
        return self._get("/stock/uspto-patent", 
        subset = subset, params=params)

    def usa_covid19(self):
        return self._get("/covid19/us")

    def fda_calendar(self):
        return self._get("/fda-advisory-committee-calendar")

    #ECONOMIC
    def country(self):
        return self._get("/country")

# %%
