from datetime import date, timedelta
import pandas as pd
import yfinance as yf

COLUMNS = ["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]

def normalize(raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Turn a yfinance history frame into our table shape."""
    if raw.empty:
        raise ValueError(f"No data returned for {ticker}")
    df = raw.reset_index()
    df["date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
    })
    df["ticker"] = ticker
    return df[COLUMNS]

def fetch_prices(ticker: str, days: int = 365) -> pd.DataFrame:
    ticker = ticker.upper().strip()
    if not ticker.replace(".", "").replace("-", "").isalnum():
        raise ValueError(f"Invalid ticker: {ticker}")
    start = date.today() - timedelta(days=days)
    raw = yf.Ticker(ticker).history(start=start.isoformat(), auto_adjust=False)
    return normalize(raw, ticker)

def save_prices(conn, df: pd.DataFrame) -> int:
    rows = df.itertuples(index=False, name=None)
    conn.executemany(
        "INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    return len(df)