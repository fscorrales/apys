# %% [markdown]
# # Alpha Vantage API

# %% [markdown]
# Get free API key in: https://www.alphavantage.co/support/#api-key
# 
# API full documentation in: https://www.alphavantage.co/documentation/
# 
# Standard API usage limit = 5 API requests per minute; 500 API requests per day

# %% [markdown]
# ## Import packages and API Key

# %%
import pandas as pd
import requests
import json
import os

if os.path.exists('alpha.json'):
    with open('alpha.json', 'r') as file:
        js = json.loads(file.read())
        TOKEN = js["token"]
        file.close()
else:
    TOKEN = ''

ENDPOINT = 'https://www.alphavantage.co/query'

# %% [markdown]
# ## API Functions

# %% [markdown]
# ### Stock Time Series

# %% [markdown]
# #### Search

# %%
def search_stock(keywords, token = TOKEN):
    function = 'SYMBOL_SEARCH'
    url = ENDPOINT
    params = {
        'function':function, 'keywords':keywords,
        'apikey':token
    }
    
    r = requests.get(url, params = params)
    data = r.json()['bestMatches']
    df = pd.DataFrame(data)
    df.columns = ['symbol', 'name', 'type', 'region', 
    'market_open', 'market_close', 'timezone', 
    'currency', 'match_score']
    return df

#Example
#data = search_stock("grupo financiero galicia") 
#data

# %% [markdown]
# #### Get intra data

# %%
def get_intra_stock(symbol, interval, 
size = "compact", token = TOKEN):

    function = 'TIME_SERIES_INTRADAY'
    url = ENDPOINT

    #outputsize = By default, outputsize=compact. Strings compact 
    # (latest 100 data points in the intraday time series) and *full* are accepted
    params = {
        'function':function, 'symbol':symbol, 'interval':interval,
        'outputsize':size, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series ('+ interval +')']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    #df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_intra_stock("AAPL", "15min", "compact")
#data.round(2).head()

# %% [markdown]
# #### Get daily data

# %%
def get_daily_stock(symbol, size = 'compact', token = TOKEN):
    function = 'TIME_SERIES_DAILY'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'outputsize':size, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series (Daily)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_daily_stock("AAPL", "compact")
#data.round(2).head()

# %% [markdown]
# #### Get daily adjusted data (PREMIUM key required)

# %%
def get_daily_adjusted_stock(symbol, size = "compact", 
token = TOKEN):
    
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'outputsize':size, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series (Daily)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 
    'adj_close', 'volume', 'div', 'split']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_daily_adjusted_stock("AAPL", "compact")
#data.round(2).head()

# %% [markdown]
# #### Get weekly data

# %%
def get_weekly_stock(symbol, token = TOKEN):
    function = 'TIME_SERIES_WEEKLY'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Weekly Time Series']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_weekly_stock("AAPL")
#data.round(2).head()

# %% [markdown]
# #### Get weekly adjusted data

# %%
def get_weekly_adjusted_stock(symbol, token = TOKEN):
    function = 'TIME_SERIES_WEEKLY_ADJUSTED'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Weekly Adjusted Time Series']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 
    'adj_close', 'volume', 'div']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_weekly_adjusted_stock("AAPL")
#data.round(2).head()

# %% [markdown]
# #### Get monthly data

# %%
def get_monthly_stock(symbol, token = TOKEN):
    function = 'TIME_SERIES_MONTHLY'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Monthly Time Series']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_monthly_stock("AAPL")
#data.round(2).head()

# %% [markdown]
# #### Get monthly adjusted data

# %%
def get_monthly_adjusted_stock(symbol, token = TOKEN):
    function = 'TIME_SERIES_MONTHLY_ADJUSTED'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Monthly Adjusted Time Series']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 
    'adj_close', 'volume', 'div']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_monthly_adjusted_stock("AAPL")
#data.round(2).head()

# %% [markdown]
# #### Get last price

# %%
def get_last_stock(symbol, token = TOKEN):
    function = 'GLOBAL_QUOTE'
    url = ENDPOINT
    params = {
        'function':function, 'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Global Quote']
    df = pd.DataFrame.from_dict(data, orient = 'index').transpose()
    df.columns = ['symbol', 'open', 'high', 'low', 'close', 'volume', 
    'date', 'previous_close', 'change', 'percent_change']
    return df

#Example
#data = get_last_stock("AAPL")
#data.round(2)

# %% [markdown]
# ### Forex (FX)

# %% [markdown]
# #### Get intra data FX

# %%
def get_intra_fx(from_fx, to_fx, interval, 
size = 'compact', token = TOKEN):
    
    function = 'FX_INTRADAY'
    url = ENDPOINT
    params = {
        'function':function,'from_symbol':from_fx,
        'to_symbol':to_fx, 'interval':interval,
        'outputsize':size, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series FX ('+ interval +')']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_intra_fx("USD", "EUR", "1min")
#data.round(4).head()

# %% [markdown]
# #### Get daily data FX

# %%
def get_daily_fx(from_fx, to_fx, 
size = "compact", token = TOKEN):
    
    function = 'FX_DAILY'
    url = ENDPOINT
    params = {
        'function':function,'from_symbol':from_fx,
        'to_symbol':to_fx,'outputsize':size, 
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series FX (Daily)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_daily_fx("USD", "ARS")
#data.round(4).head()

# %% [markdown]
# #### Get weekly data FX

# %%
def get_weekly_fx(from_fx, to_fx, 
token = TOKEN):
    
    function = 'FX_WEEKLY'
    url = ENDPOINT
    params = {
        'function':function,'from_symbol':from_fx,
        'to_symbol':to_fx, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series FX (Weekly)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_weekly_fx("USD", "ARS")
#data.round(4).head()

# %% [markdown]
# #### Get monthly data FX

# %%
def get_monthly_fx(from_fx, to_fx, 
token = TOKEN):
    
    function = 'FX_MONTHLY'
    url = ENDPOINT
    params = {
        'function':function,'from_symbol':from_fx,
        'to_symbol':to_fx, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series FX (Monthly)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = get_monthly_fx("USD", "ARS")
#data.round(4).head()

# %% [markdown]
# #### Get last price FX

# %%
def get_last_fx(from_fx, to_fx, token = TOKEN):
    function = 'CURRENCY_EXCHANGE_RATE'
    url = ENDPOINT
    params = {
        'function':function, 'from_currency':from_fx,
        'to_currency':to_fx, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Realtime Currency Exchange Rate']
    df = pd.DataFrame.from_dict(data, orient = 'index').transpose()
    df.columns = ['from_code', 'from_name', 'to_code', 
    'to_name', 'exchange_rate', 'last_refresh', 
    'timezone', 'bid_price', 'ask_price']
    return df

#Example
#data = get_last_fx('USD', 'ARS')
#data

# %% [markdown]
# ### Crypto

# %% [markdown]
# #### Ranking (no funciona)

# %%
def rank_cryto(symbol, token = TOKEN):
    function = 'CRYPTO_RATING'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()#['Time Series FX ('+ interval +')']
    #df = pd.DataFrame.from_dict(data, orient = 'index')
    #df = df.astype('float')
    #df.index.name = 'date'
    #df.columns = ['open', 'high', 'low', 'close']
    #df = df.sort_values('date', ascending = True)
    #df.index = pd.to_datetime(df.index)
    return r

#Example
#data = rank_cryto("BTC")


# %% [markdown]
# #### Get intraday crypto

# %%
def get_intra_crypto(symbol, interval, market = 'USD',
size = 'compact', token = TOKEN):
    
    function = 'CRYPTO_INTRADAY'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'market':market, 'interval':interval,
        'outputsize':size, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series Crypto ('+ interval +')']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df 

#Example
#data = get_intra_crypto("BTC", "5min")
#data.round(4).head()

# %% [markdown]
# #### Get daily crypto

# %%
def get_daily_crypto(symbol, market = 'USD',
token = TOKEN):
    
    function = 'DIGITAL_CURRENCY_DAILY'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'market':market,'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series (Digital Currency Daily)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    #df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df 

#Example
#data = get_daily_crypto("BTC")
#data.round(4).head()

# %% [markdown]
# #### Get weekly data crypto

# %%
def get_weekly_crypto(symbol, market = 'USD',
token = TOKEN):
    
    function = 'DIGITAL_CURRENCY_WEEKLY'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'market':market,'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series (Digital Currency Weekly)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    #df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df 

#Example
#data = get_weekly_crypto("BTC")
#data.round(4).head()

# %% [markdown]
# #### Get monthly data crypto

# %%
def get_monthly_crypto(symbol, market = 'USD',
token = TOKEN):
    
    function = 'DIGITAL_CURRENCY_MONTHLY'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'market':market,'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Time Series (Digital Currency Monthly)']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    #df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df 

#Example
#data = get_monthly_crypto("BTC")
#data.round(4).head()

# %% [markdown]
# #### Get last price crypto

# %%
def get_last_crypto(from_crypto, to_crypto, 
token = TOKEN):
    function = 'CURRENCY_EXCHANGE_RATE'
    url = ENDPOINT
    params = {
        'function':function, 'from_currency':from_crypto,
        'to_currency':to_crypto, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Realtime Currency Exchange Rate']
    df = pd.DataFrame.from_dict(data, orient = 'index').transpose()
    df.columns = ['from_code', 'from_name', 'to_code', 
    'to_name', 'exchange_rate', 'last_refresh', 
    'timezone', 'bid_price', 'ask_price']
    return df

#Example
#data = get_last_crypto('BTC', 'USDT')
#data

# %% [markdown]
# ### USA Economic indicators

# %% [markdown]
# #### Real GDP

# %% [markdown]
# #### Real GDP per capita

# %% [markdown]
# #### Treasure Yield

# %% [markdown]
# #### Federal Funds (interest) Rate

# %% [markdown]
# #### CPI

# %% [markdown]
# #### Inflation

# %% [markdown]
# #### Inflations expectation

# %% [markdown]
# #### Consumer Sentiment

# %% [markdown]
# #### Retail Sales

# %% [markdown]
# #### Durable Goods Orderes

# %% [markdown]
# #### Unemployment rate

# %% [markdown]
# #### Nonfarm Playroll

# %% [markdown]
# ### Technical Indicators

# %% [markdown]
# #### General Moving Average (mov_type)

# %%
def mov_avg(symbol, time_period, mov_type = "sma",
interval = "5min", series_type= "close", token = TOKEN):

    function = mov_type.upper()
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'interval':interval,'series_type':series_type,
        'time_period':time_period, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Technical Analysis: '+ function]
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = mov_avg('AAPL', 50)
#data

# %% [markdown]
# #### Simple moving average (SMA)

# %%
def sma(symbol, time_period, interval = "5min", 
series_type= "close", token = TOKEN):

    function = 'SMA'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'interval':interval,'series_type':series_type,
        'time_period':time_period, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Technical Analysis: SMA']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = sma('AAPL', 50)
#data

# %% [markdown]
# #### Exponential moving average (EMA)

# %%
def ema(symbol, time_period, interval = "5min", 
series_type= "close", token = TOKEN):

    function = 'EMA'
    url = ENDPOINT
    params = {
        'function':function,'symbol':symbol,
        'interval':interval,'series_type':series_type,
        'time_period':time_period, 'apikey':token
    }

    r = requests.get(url, params = params)
    data = r.json()['Technical Analysis: EMA']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df = df.astype('float')
    df.index.name = 'date'
    df = df.sort_values('date', ascending = True)
    df.index = pd.to_datetime(df.index)
    return df

#Example
#data = ema('AAPL', 50)
#data

# %% [markdown]
# #### Weighted moving average (WMA)

# %% [markdown]
# #### Double exponential moving average (DEMA)

# %% [markdown]
# #### Triple exponential moving average (TEMA)

# %% [markdown]
# #### Triangular moving average (TRIMA)

# %% [markdown]
# #### Kaufman adaptive moving average (KAMA)

# %% [markdown]
# #### MESA adaptive moving average (MAMA)

# %% [markdown]
# #### Volume weighted average price (VWAP) (Premium)

# %% [markdown]
# #### Triple exponential moving average (T3)

# %% [markdown]
# #### Moving average convergence / divergence (MACD) (Premium)

# %% [markdown]
# #### Moving average convergence / divergence values with controllable moving average type (MACDEXT)

# %% [markdown]
# #### Stochastic oscillator (STOCH)

# %% [markdown]
# #### Stochastic fast (STOCHF)

# %% [markdown]
# #### Relative strength index (RSI)

# %% [markdown]
# #### Stochastic relative strength index (STOCHRSI)

# %% [markdown]
# #### Williams' %R (WILLR)

# %% [markdown]
# #### Average directional movement index (ADX)

# %% [markdown]
# #### Average directional movement index rating (ADXR)

# %% [markdown]
# #### Absolute price oscillator (APO)

# %% [markdown]
# #### Percentage price oscillator (PPO)

# %% [markdown]
# #### Momentum (MOM)

# %% [markdown]
# #### Commodity channel index (CCI)

# %% [markdown]
# #### Rate of change (ROC)

# %% [markdown]
# #### Rate of change ratio (ROCR)

# %% [markdown]
# #### Money flow index (MFI)

# %% [markdown]
# #### Triple smooth exponential moving average (TRIX)

# %% [markdown]
# #### Directional movement index (DX)

# %% [markdown]
# #### Minus directional indicator (MINUS_DI)

# %% [markdown]
# #### Plus directional indicator (PLUS_DI)

# %% [markdown]
# #### Minus directional movement (MINUS_DM)

# %% [markdown]
# #### Plus directional movement (PLUS_DM)

# %% [markdown]
# #### Bollinger bands (BBANDS) (Premium)

# %% [markdown]
# #### Parabolic SAR (SAR)

# %% [markdown]
# #### Balance volume (OBV)


