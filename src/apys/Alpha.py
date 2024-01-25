'''
At Alpha Vantage, the majority of our API endpoints can be accessed for free. 
For use cases that exceed our standard API usage limit (25 API requests per day) 
or require certain premium API functions, we offer a premium plan to scale your 
use cases
'''

# %%
import json
import io
import requests
import pandas as pd

from Exceptions import APIException
from Exceptions import APIRequestException


class Alpha:
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

    #GET STOCK DATA
    def stock_search(self, keywords, 
    subset = "bestMatches", output_df = True):
        function = 'SYMBOL_SEARCH'
        params = {
            'function':function, 'keywords':keywords,
        }
        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            df.columns = ['symbol', 'name', 'type', 'region', 
            'market_open', 'market_close', 'timezone', 
            'currency', 'match_score']
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_intra(self, symbol, 
    interval = "15min", size = "compact",
    subset = True, output_df = True):
        function = 'TIME_SERIES_INTRADAY'
        #outputsize = By default, outputsize=compact. Strings compact 
        # (latest 100 data points in the intraday time series) and *full* are accepted
        params = {
            'function':function, 'symbol':symbol, 
            'interval':interval, 'outputsize':size
        }
        data = self._get("", params=params)

        if subset == True:
            subset = 'Time Series ('+ interval +')'
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.sort_values('date', ascending = True)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_daily(self, symbol, size = 'compact',
    subset = 'Time Series (Daily)', output_df = True):
        function = 'TIME_SERIES_DAILY'
        params = {
        'function':function, 'symbol':symbol,
        'outputsize':size
        }
        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_daily_adjusted(self, symbol, size = "compact", 
    subset = 'Time Series (Daily)', output_df = True):
        
        '''
        Tip: this is a premium API function. 
        There are multiple ways to unlock premium endpoints:
            - Become a holder of Alpha Vantage Coin (AVC), 
            a Ethereum-based cryptocurrency that provides a
            variety of utility & governance functions for 
            the Alpha Vantage ecosystem (AVC mining guide),
            to unlock all premium API endpoints.
            - Subscribe to any of the premium membership 
            plans to instantly unlock all premium endpoints.
        '''
        function = 'TIME_SERIES_DAILY_ADJUSTED'
        params = {
            'function':function, 'symbol':symbol,
            'outputsize':size
        }
        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 
            'adj_close', 'volume', 'div', 'split']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_weekly(self, symbol, 
    subset = 'Weekly Time Series', output_df = True):
        function = 'TIME_SERIES_WEEKLY'
        params = {
            'function':function, 'symbol':symbol
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_weekly_adjusted(self, symbol, 
    subset = 'Weekly Adjusted Time Series', output_df = True):
        function = 'TIME_SERIES_WEEKLY_ADJUSTED'
        params = {
            'function':function, 'symbol':symbol
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 
            'adj_close', 'volume', 'div']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_monthly(self, symbol, 
    subset = 'Monthly Time Series', output_df = True):
        function = 'TIME_SERIES_MONTHLY'
        params = {
            'function':function, 'symbol':symbol
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_monthly_adjusted(self, symbol, 
    subset = 'Monthly Adjusted Time Series', output_df = True):
        function = 'TIME_SERIES_MONTHLY_ADJUSTED'
        params = {
            'function':function, 'symbol':symbol
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 
            'adj_close', 'volume', 'div']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_quote(self, symbol, 
    subset = 'Global Quote', output_df = True):
        function = 'GLOBAL_QUOTE'
        params = {
            'function':function, 'symbol':symbol,
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index').transpose()
            df.columns = ['symbol', 'open', 'high', 'low', 'close', 'volume', 
            'date', 'previous_close', 'change', 'percent_change']
            self.data = df
        else:
            self.data = data
        return self.data

    #GET PHYSICAL AND DIGITAL (CRYPTO) LIST
    def fx_physical_currency(self):
        URL = "https://www.alphavantage.co/physical_currency_list/"
        r = requests.get(URL)
        data = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        data.columns = ["code", "description"]
        self.data = data
        return self.data

    def fx_crypto_currency(self):
        URL = "https://www.alphavantage.co/digital_currency_list/"
        r = requests.get(URL)
        data = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        data.columns = ["code", "description"]
        self.data = data
        return self.data

    #GET FOREX (FX) DATA
    def fx_intra(self, from_fx, to_fx, interval = "15min", 
    size = 'compact', subset = True, output_df = True):
        function = 'FX_INTRADAY'
        params = {
            'function':function,'from_symbol':from_fx,
            'to_symbol':to_fx, 'interval':interval,
            'outputsize':size
        }
        data = self._get("", params=params)

        if subset == True:
            subset = 'Time Series FX ('+ interval +')'
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def fx_daily(self, from_fx, to_fx, size = "compact",
    subset = 'Time Series FX (Daily)', output_df = True):
        function = 'FX_DAILY'
        params = {
            'function':function,'from_symbol':from_fx,
            'to_symbol':to_fx,'outputsize':size
        }
        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def fx_weekly(self, from_fx, to_fx,
    subset = 'Time Series FX (Weekly)', output_df = True):
        function = 'FX_WEEKLY'
        params = {
            'function':function,'from_symbol':from_fx,
            'to_symbol':to_fx
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def fx_monthly(self, from_fx, to_fx,
    subset = 'Time Series FX (Monthly)', output_df = True):
        function = 'FX_MONTHLY'
        params = {
            'function':function,'from_symbol':from_fx,
            'to_symbol':to_fx
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def fx_quote(self, from_fx, to_fx,
    subset = 'Realtime Currency Exchange Rate',
    output_df = True):
        function = 'CURRENCY_EXCHANGE_RATE'
        params = {
            'function':function, 'from_currency':from_fx,
            'to_currency':to_fx
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index').transpose()
            df.columns = ['from_code', 'from_name', 'to_code', 
            'to_name', 'exchange_rate', 'last_refresh', 
            'timezone', 'bid_price', 'ask_price']
            self.data = df
        else:
            self.data = data
        return self.data

    #GET DIGITAL (CRYPTO) DATA
    def crypto_intra(self, symbol, interval = "15min", 
    physical_currency = "USD",size = 'compact', 
    subset = True, output_df = True):
        function = 'CRYPTO_INTRADAY'
        params = {
            'function':function,'symbol':symbol,
            'market':physical_currency, 'interval':interval,
            'outputsize':size
        }
        data = self._get("", params=params)

        if subset == True:
            subset = 'Time Series Crypto ('+ interval +')'
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def crypto_daily(self, symbol, physical_currency = "USD",
    subset = 'Time Series (Digital Currency Daily)', 
    output_df = True):
        function = 'DIGITAL_CURRENCY_DAILY'
        params = {
            'function':function,'symbol':symbol,
            'market':physical_currency
        }
        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            fiat = physical_currency.lower()
            df.columns = ['open_' + fiat, 'open_usd', 
            'high_' + fiat, 'high_usd',
            'low_' + fiat, 'low_usd',
            'close_' + fiat, 'close_usd',
            'volume', 'market_cap_usd']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def crypto_weekly(self, symbol, physical_currency = "USD",
    subset = 'Time Series (Digital Currency Weekly)', 
    output_df = True):
        function = 'DIGITAL_CURRENCY_WEEKLY'
        params = {
            'function':function,'symbol':symbol,
            'market':physical_currency
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            fiat = physical_currency.lower()
            df.columns = ['open_' + fiat, 'open_usd', 
            'high_' + fiat, 'high_usd',
            'low_' + fiat, 'low_usd',
            'close_' + fiat, 'close_usd',
            'volume', 'market_cap_usd']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def crypto_monthly(self, symbol, physical_currency = 'USD',
    subset = 'Time Series (Digital Currency Monthly)',
    output_df = True):
        function = 'DIGITAL_CURRENCY_MONTHLY'
        params = {
            'function':function,'symbol':symbol,
            'market':physical_currency
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            fiat = physical_currency.lower()
            df.columns = ['open_' + fiat, 'open_usd', 
            'high_' + fiat, 'high_usd',
            'low_' + fiat, 'low_usd',
            'close_' + fiat, 'close_usd',
            'volume', 'market_cap_usd']
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def crypto_quote(self, from_crypto, to_crypto,
    subset = 'Realtime Currency Exchange Rate',
    output_df = True):
        return self.fx_quote(from_fx = from_crypto,
        to_fx= to_crypto, subset=subset, output_df=output_df)

    #GET USA ECONOMIC DATA (not yet available)


    #GET TECHNICAL INDICATORS
    def mov_avg(self, symbol, time_period = 14,
    mov_type = "sma", interval = "5min", 
    series_type= "close", subset = True, 
    output_df = True):
        function = mov_type.upper()
        params = {
            'function':function,'symbol':symbol,
            'interval':interval,'series_type':series_type,
            'time_period':time_period
        }

        data = self._get("", params=params)

        if subset == True:
            subset = 'Technical Analysis: '+ function
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def sma(self, symbol, time_period = 14, 
    interval = "5min", series_type= "close", 
    subset = 'Technical Analysis: SMA',
    output_df = True):
        function = 'SMA'
        params = {
            'function':function,'symbol':symbol,
            'interval':interval,'series_type':series_type,
            'time_period':time_period
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

    def ema(self, symbol, time_period = 14, 
    interval = "5min", series_type= "close", 
    subset = 'Technical Analysis: EMA',
    output_df = True):
        function = 'EMA'
        params = {
            'function':function,'symbol':symbol,
            'interval':interval,'series_type':series_type,
            'time_period':time_period
        }

        data = self._get("", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame.from_dict(data, orient = 'index')
            df = df.astype('float')
            df.index.name = 'date'
            df = df.sort_values('date', ascending = True)
            df.index = pd.to_datetime(df.index)
            self.data = df
        else:
            self.data = data
        return self.data

# %%
