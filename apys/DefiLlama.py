# %%
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

from Exceptions import APIException
from Exceptions import APIRequestException


class DefiLlama:
    data = None
    API_URL = "https://api.llama.fi"
    DEFAULT_TIMEOUT = 10

    def __init__(self, proxies = None):
        self._session = self._init_session(proxies)

    @staticmethod
    def _init_session(proxies):
        session = requests.session()
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
    
    def _post(self, path, **kwargs):
        return self._request("post", path, **kwargs)

    #GET GENERIC FUNCTION
    def get_generic(self, endpoint = "", 
    subset = None, **params):
        return self._get(endpoint, params=params)

    #TVL
    ##Get list all DeFi protocols across all blockchains
    def protocols(self, output_df = True):
        data = self._get("/protocols")
        if output_df == True:
            df = pd.DataFrame(data)
            df.set_index('name', inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    ##Get metrics and historic TVL for one DeFi dApp
    def protocol(self, protocol, output_df = True):
        data = self._get("/protocol/" + protocol)
        if output_df == True:
            tvl = pd.DataFrame(data["tvl"])
            tvl.date = pd.to_datetime(tvl.date, unit='s')
            tvl = tvl.set_index('date')
            del data['tvl']

            chain_tvls = {}
            for k, v in data["chainTvls"].items():
                chain_tvls[k] = pd.DataFrame(v["tvl"])
                chain_tvls[k].date = pd.to_datetime(chain_tvls[k].date, unit='s')
                chain_tvls[k] = chain_tvls[k].set_index('date')
            chain_tvls = pd.concat(chain_tvls)
            del data['chainTvls']

            if len(data["currentChainTvls"]) > 0:
                current_chain_tvls = pd.DataFrame.from_dict(
                    data["currentChainTvls"], orient="index")
                current_chain_tvls.columns = ["tvl"]
            else:
                current_chain_tvls = None
            del data['currentChainTvls']
            
            if len(data.get("tokensInUsd", "")) > 0:
                ans = []
                for i in data["tokensInUsd"]:
                    i["tokens"]["date"] = i["date"]
                    ans.append(i["tokens"])
                tokens_usd = pd.DataFrame(ans)
                tokens_usd.date = pd.to_datetime(tokens_usd.date, unit='s')
                tokens_usd = tokens_usd.set_index('date')
                del data['tokensInUsd']
            else:
                tokens_usd = None
            
            if len(data.get("tokens", "")) > 0:
                ans = []
                for i in data["tokens"]:
                    i["tokens"]["date"] = i["date"]
                    ans.append(i["tokens"])
                tokens = pd.DataFrame(ans)
                tokens.date = pd.to_datetime(tokens.date, unit='s')
                tokens = tokens.set_index('date')
                del data['tokens']
            else:
                tokens = None

            metadata = data
            self.data = {
                "metadata":metadata, "tvl":tvl,
                "chain_tvls":chain_tvls, 
                "current_chain_tvls":current_chain_tvls,
                "tokens_usd":tokens_usd, "tokens":tokens
                }
        else:
            self.data = data
        return self.data

    ##Plot historical TVL vy exchange
    def plot_historical_tvl(self, *protocols):

        if protocols == ():
            exchanges = ['pancakeswap', 'curve', 'makerdao',
            'uniswap','Compound', 'AAVE','sushiswap','anchor']
        else:
            exchanges = protocols

        hist = [self.protocol(exchange)['tvl'] for exchange in exchanges]
        df = pd.concat(hist, axis=1)
        df.columns = exchanges

        df.plot(figsize=(12,6))

    ##Get historical TVL across all DeFi dApps,
    ##cummulative result
    def charts(self, output_df = True):
        data = self._get("/charts")
        if output_df == True:
            df = pd.DataFrame(data)
            df.date = pd.to_datetime(df.date, unit='s')
            df.set_index('date', inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data
    
    ##Top dapps TVL by chain
    def plot_top_dapps_tvl(self, n_dapp = 50):
        df = self.protocols()
        fig, ax = plt.subplots(figsize=(12,6))

        n = n_dapp # quantity to show
        top = df.sort_values('tvl', ascending=False).head(n)

        chains = top.groupby('chain').size().index.values.tolist()
        for chain in chains:
            filtro = top.loc[top.chain==chain]
            ax.bar(filtro.index, filtro.tvl, label=chain)

        ax.set_title(f'Top {n} dApp TVL, groupBy dApp main Chain', fontsize=14)
        ax.grid(alpha=0.5)
        plt.legend()
        plt.xticks(rotation=90)
        plt.show()

    ##Get historical TVL across all DeFi dApps,
    ##cummulative result
    def chart_chain(self, chain, output_df = True):
        data = self._get("/charts/" + chain)

        if output_df == True:
            df = pd.DataFrame(data)
            df.date = pd.to_datetime(df.date, unit='s')
            df.set_index('date', inplace=True)
            self.data = df
        else:
            self.data = data
        return self.data

    ##Get current TVL of specific protocol
    def protocol_tvl(self, protocol, output_df = True):
        data = self._get("/tvl/" + protocol)

        self.data = data
        return self.data

    ##Get current TVL of all chains
    def chains_tvl(self, output_df = True):
        data = self._get("/chains")
        if output_df == True:
            df = pd.DataFrame(data)
            self.data = df
        else:
            self.data = data
        return self.data
    
    #COINS
    ##Get current or historical price of tokens 
    ## by contract address
