import yfinance as yf
import pandas as pd
from . import parquet_cache


def download_yf(
    symbols, period="6mo", interval="1h", price_type="Close", cache=True, outdir="data"
) -> pd.DataFrame:
    """
    Henter historiske data fra Yahoo Finance for én eller flere tickere.
    Rydder opp i MultiIndex og returnerer et rent DataFrame.

    Args:
        symbols (str | list[str]): Ticker eller liste av tickere, f.eks. "BTC-USD" eller ["BTC-USD", "ETH-USD"]
        period (str): Hvor langt tilbake, f.eks. "1y", "6mo", "3mo"
        interval (str): Tidsintervall, f.eks. "1h", "4h", "1d"
        price_type (str): Felt som beholdes ved flere tickere ("Close", "Open", osv.)
        save_csv (bool): Lagre CSV automatisk
        outdir (str): Katalog for CSV-filer
    Returns:
        pd.DataFrame: Data med kolonner = tickere, rader = tidsstempel
    """

    # Normaliser filnavn
    fname = "-".join(symbols) if isinstance(symbols, list) else symbols
    filepath = outdir + "\\" + f"{fname}_{interval}"
    data = parquet_cache.read_parquet_cache(filepath, max_age_s=600)

    # Hent data
    data = yf.download(
        symbols, period=period, interval=interval, group_by="ticker", progress=False
    )
    if data is None:
        raise NameError(f"Ticker: {symbols} error")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(0)

    # Lagre til parquet cache
    parquet_cache.write_parquet_cache(
        data,
        filepath,
        symbols=symbols,
        interval=interval,
        period=period,
    )

    return data


def get_symbol_data(symbol, period, interval):
    try:
        data = download_yf(symbol, period=period, interval=interval)
        if not data.empty:
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else data.iloc[-1]
            change = ((latest["Close"] - previous["Close"]) / previous["Close"] * 100)
            return {
                "price": latest["Close"],
                "change": change,
                "high": data["High"].max(),
                "low": data["Low"].min(),
                "data": data
            }
    except Exception:
        pass
    return None