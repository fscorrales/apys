# %%
import fct.alpha_fct as alpha

# %%
class Alpha:
    data = None
    _ENDPOINT = 'https://www.alphavantage.co/query'

    @property
    def ENDPOINT(self):
        return self._ENDPOINT

    def __init__(self, token) -> None:
        self.token = token

    def get_intra_stock(self, symbol, interval, 
    size = "compact"):
        self.data = alpha.get_intra_stock(symbol, interval,
        size, self.token)
        return self.data.head().round(2)

# %%
