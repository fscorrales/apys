import datetime as dt
from connect import IOL
from dataclasses import dataclass

@dataclass
class StockDaily:
    IOL: IOL
    symbol: str
    from_date: dt.date
    to_date: dt.date = dt.date.today()
    market: str = 'bCBA'
    adjusted: bool = False

    def stock_daily(self):
        self.IOL.update_token()
        h = {
            "Authorization":"Bearer " + self.IOL.token["access_token"]
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