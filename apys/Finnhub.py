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
    
    def _get(self, path = None, **kwargs):
        return self._request("get", path, **kwargs)

    @property
    def api_key(self):
        return self._session.params.get("token")

    @api_key.setter
    def api_key(self, api_key):
        self._session.params["token"] = api_key

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", **params):
        return self._get(endpoint, params=params)

    #STOCK FUNDAMENTALS
    def symbol_lookup(self, query, 
    subset = "result", output_df = True):
        params = {"q": query}
        data = self._get("/search", params=params)
        
        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_exchanges(self):
        URL = "https://docs.google.com/spreadsheets/d/1I3pBxjfXB056-g_JYf_6o3Rns3BV2kMGG1nCatb91ls/edit#gid=0"
        URL_OK = URL.replace('edit#', 'export?')
        data = pd.read_csv(URL_OK + '&format=csv',
        usecols=[i for i in range(0,9)])
        data.columns.values[8] = "observations"
        self.data = data
        return self.data

    def stock_symbols(self, exchange,
    output_df = True,**kwargs):
        params = {"exchange": exchange, **kwargs}
        data = self._get("/stock/symbol", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data


    def company_profile(self, **params):
        #Premium access required
        return self._get("/stock/profile", params=params)

    def company_profile2(self, symbol = None, isin = None,
    cusip = None, output_df = True, **kwargs):
        params = {"symbol": symbol, "isin": isin,
        "cusip": cusip, **kwargs}
        data = self._get("/stock/profile2", params=params)

        if output_df == True:
            df = pd.DataFrame(data, index = [0]).set_index(["ticker"])
            self.data = df
        else:
            self.data = data
        return self.data

    def market_news(self, category = "crypto",
    minId = 0, output_df = True, **kwargs):
        #category = This parameter can be 1 of the following 
        #values general, forex, crypto, merger.
        params = {"category": category,
        "minId":minId, **kwargs}
        data = self._get("/news", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df["datetime"] = pd.to_datetime(df.datetime, unit='s')
            self.data = df
        else:
            self.data = data
        return self.data


    def company_news(self, symbol, from_date,
    to_date, output_df = True):
        params = {"symbol":symbol, 
                "from":from_date, "to":to_date}
        data = self._get("/company-news", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df["datetime"] = pd.to_datetime(df.datetime, unit='s')
            self.data = df
        else:
            self.data = data
        return self.data

    def peers(self, symbol, output_df = True):
        params = {"symbol": symbol}
        data = self._get("/stock/peers", params=params)

        if output_df == True:
            df = pd.DataFrame(data, columns=[symbol])
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_basic_financials(self, symbol, 
    metric = "all", subset = "metric", output_df = True):
        #metric = This parameter can be 1 of the following 
        #all, price, growth, margin, management, 
        #financialStrength, perShare.
        params = {"symbol":symbol, "metric":metric}
        data = self._get("/stock/metric", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data, index = [symbol])
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_insider_transactions(self, symbol, 
    from_date=None, to_date=None, subset = "data",
    output_df = True):
        params = {"symbol":symbol, 
                "from":from_date, "to":to_date}
        data = self._get("/stock/insider-transactions", 
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data

    def financials_reported(self, symbol = None, 
    cik = None, accessNumber = None, freq = "annual",
    subset = "data", output_df = True, **kwargs):
        #Frequency. Can be either annual or quarterly
        params = {"symbol":symbol, "cik":cik,
        "accessNumber":accessNumber, 
        "freq":freq, **kwargs}
        data = self._get("/stock/financials-reported",
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = []
            for i in data:
                data_filter = {k: i[k] for k in list(i)[:-1]}
                reports = {}
                for k in i["report"]:
                    reports[k] = pd.DataFrame(i["report"][k]).set_index(["label"])
                reports = pd.concat(reports)
                df.append(reports.join(pd.DataFrame(
                    data_filter, index=reports.index
                )))
            df = pd.concat(df).reset_index()
            df.rename({'level_0': 'fs'}, axis=1, inplace=True)
            df.set_index(["symbol", "year", "quarter", 
            "fs", "label"], inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    def sec_filings(self, symbol = None, cik = None, 
    accessNumber = None, form = None, from_date=None, 
    to_date=None, output_df = True, **kwargs):
        params = {"symbol":symbol, "cik":cik,
        "accessNumber":accessNumber, "form":form,
        "from":from_date, "to":to_date, **kwargs}
        data = self._get("/stock/filings", params=params)

        if output_df == True:
            self.data = pd.DataFrame(data)
        else:
            self.data = data
        return self.data

    def ipo_calendar(self, from_date, to_date, 
    subset = "ipoCalendar", output_df = True):
        params = {"from":from_date, "to":to_date}
        data = self._get("/calendar/ipo", 
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            self.data = pd.DataFrame(data)
        else:
            self.data = data
        return self.data

    #STOCK ESTIMATES
    def recommendation_trends(self, symbol, 
    output_df = True):
        params = {"symbol":symbol}
        data = self._get("/stock/recommendation", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df['period'] = pd.to_datetime(df.period)
            df.set_index('period', inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    def recommendation_rank(self, symbol):
        df = self.recommendation_trends(symbol)
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

    def eps_surprises(self, symbol, limit=None, 
    output_df = True):
        params = {"symbol": symbol, "limit": limit}
        data = self._get("/stock/earnings", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df['period'] = pd.to_datetime(df.period)
            self.data = df
        else:
            self.data = data
        return self.data

    def earnings_calendar(self, symbol = None,
    from_date = None, to_date = None, international = False,
    subset = "earningsCalendar", output_df = True,
    **kwargs):
        params = {"symbol":symbol, "from":from_date, 
        "to":to_date, "international":international, 
        **kwargs}
        data = self._get("/calendar/earnings", 
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df.date)
            self.data = df
        else:
            self.data = data
        return self.data

    #STOCK PRICE
    def stock_quote(self, symbol, output_df = True):
        params = {"symbol":symbol}
        data = self._get("/quote", params=params)

        if output_df == True:
            df = pd.DataFrame(data, index = [symbol])
            df.columns = ["close", "change", "pct_change",
            "high", "low", "open", "prev_close", "date"]
            df.date = pd.to_datetime(df.date, unit='s')
            self.data = df
        else:
            self.data = data
        return self.data

    def stock_candles(self, symbol, from_date, to_date, 
    resolution = "D", adj = True, output_df = True):
        #resolution = Supported resolution includes 
        # 1, 5, 15, 30, 60, D, W, M .Some timeframes 
        # might not be available depending on the exchange.
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date),
                "adjusted":adj}
        data = self._get("/stock/candle", 
        params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df.columns = ["close","high", "low", "open", 
            "status", "date", "volume"]
            df.date = pd.to_datetime(df.date, unit='s')
            df.set_index("date", drop=True, inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    #ETFS & INDICES
    def indices(self):
        URL = "https://docs.google.com/spreadsheets/d/1Syr2eLielHWsorxkDEZXyc55d6bNx1M3ZeI4vdn7Qzo/edit#gid=0"
        URL_OK = URL.replace('edit#', 'export?')
        data = pd.read_csv(URL_OK + '&format=csv',
        usecols=[i for i in range(0,2)])
        self.data = data
        return self.data

    def indices_constituents(self, symbol, 
    subset = "constituents", output_df = True):
        params = {"symbol":symbol}
        data = self._get("/index/constituents", 
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data        


    #FOREX
    def forex_exchanges(self, output_df = True):
        params = {}
        data = self._get("/forex/exchange", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data           

    def forex_symbols(self, exchange, output_df = True):
        params = {"exchange":exchange}
        data =  self._get("/forex/symbol", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data   

    #CRYPTO
    def crypto_exchanges(self, output_df = True):
        params = {}
        data = self._get("/crypto/exchange", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data   

    def crypto_symbols(self, exchange, output_df = True):
        params = {"exchange":exchange}
        data = self._get("/crypto/symbol", params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data   

    def crypto_candles(self, symbol, from_date, to_date, 
    resolution = "D", output_df = True):
        #Supported resolution includes 
        # 1, 5, 15, 30, 60, D, W, M.
        # Some timeframes might not be 
        # available depending on the exchange.
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date)}
        data = self._get("/crypto/candle",
        params=params)

        if output_df == True:
            df = pd.DataFrame(data)
            df.columns = ["close","high", "low", "open", 
            "status", "date", "volume"]
            df.date = pd.to_datetime(df.date, unit='s')
            df.set_index("date", drop=True, inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    #TECHNICAL ANALYSIS
    def indicators(self):
        URL = "https://docs.google.com/spreadsheets/d/1ylUvKHVYN2E87WdwIza8ROaCpd48ggEl1k5i5SgA29k/edit#gid=0"
        URL_OK = URL.replace('edit#', 'export?')
        data = pd.read_csv(URL_OK + '&format=csv',
        usecols=[i for i in range(0,4)])
        df = {}
        df["indicators"] = data.iloc[:-14]
        df["indicators"].columns = ["technical_indicator",
        "description", "arguments", "response_attributes"]
        df["indicators"].set_index(["technical_indicator"],
        inplace=True)
        df["apendix"] = data.tail(9)
        df["apendix"].drop(["Arguments", "Response Attributes"], 
        axis = 1, inplace = True)
        df["apendix"].columns = ["code", "ma_type"]
        df["apendix"].set_index(["code"], inplace=True)
        self.data = df
        return self.data

    def technical_indicator(self, symbol, from_date, to_date, 
    indicator, resolution = "D", subset = None, 
    output_df = True, **indicator_fields):
        from_date = dt.timestamp(dt.strptime(from_date, '%Y-%m-%d'))
        to_date = dt.timestamp(dt.strptime(to_date, '%Y-%m-%d'))
        params = {"symbol":symbol, "resolution":resolution,
                "from":int(from_date), "to":int(to_date),
                "indicator":indicator, **indicator_fields}
        data = self._get("/indicator", params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            df.rename(columns = {"c":"close","h":"high",
            "l":"low", "o":"open", "s":"status", 
            "t":"date", "v":"volume"}, inplace=True)
            df.date = pd.to_datetime(df.date, unit='s')
            df.set_index("date", drop=True, inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data  

    #ALTERNATIVE DATA
    def stock_social_sentiment(self, symbol, 
    from_date=None, to_date=None, output_df = True):
        params = {"symbol":symbol, "from":from_date, 
                "to":to_date}
        data = self._get("/stock/social-sentiment", 
        params=params)

        if output_df == True:
            reddit = pd.DataFrame(data["reddit"])
            reddit["source"] = "reddit"
            twitter = pd.DataFrame(data["twitter"])
            twitter["source"] = "twitter"
            df = pd.concat([reddit, twitter])
            df.columns = ["time", "mention", "pos_score",
            "neg_score", "pos_mention", "neg_mention",
            "final_score", "source"]
            df["time"] = pd.to_datetime(df["time"])
            self.data = df
        else:
            self.data = data
        return self.data  

    def stock_uspto_patents(self, symbol, from_date, 
    to_date, subset = "data", output_df = True):
        params = {"symbol":symbol, "from":from_date, 
                "to":to_date}
        data = self._get("/stock/uspto-patent", 
        params=params)

        if subset != None:
            data = data[subset]

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data  

    def usa_covid19(self, output_df = True):
        data = self._get("/covid19/us")

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data  

    def fda_calendar(self, output_df = True):
        data = self._get("/fda-advisory-committee-calendar")

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data  

    #ECONOMIC
    def country(self, output_df = True):
        data = self._get("/country")

        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data  

# %%
