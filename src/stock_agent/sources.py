import io
from datetime import date, timedelta

import pandas as pd
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from .prices import COLUMNS, fetch_prices
from .ratelimit import TokenBucket


class TransientError(Exception):
    """A temporary failure (rate limit, network). Worth retrying or falling back."""


yahoo_limiter = TokenBucket(rate_per_sec=1, capacity=3)
stooq_limiter = TokenBucket(rate_per_sec=1, capacity=2)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(TransientError),
    reraise=True,
)
def fetch_yahoo(ticker: str, days: int) -> pd.DataFrame:
    yahoo_limiter.acquire()
    try:
        return fetch_prices(ticker, days)
    except ValueError:
        raise  # invalid ticker or empty data: retrying won't help
    except Exception as e:
        raise TransientError(str(e)) from e


def parse_stooq(text: str, ticker: str, days: int) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.StringIO(text))
    except Exception as e:
        raise ValueError(f"Unreadable Stooq response for {ticker}") from e
    if df.empty or "Date" not in df.columns:
        raise ValueError(f"Stooq returned no data for {ticker}")

    df = df.rename(columns=str.lower)
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    df = df[df["date"] >= cutoff].copy()
    if df.empty:
        raise ValueError(f"Stooq has no recent data for {ticker}")

    df["ticker"] = ticker
    df["adj_close"] = df["close"]  # Stooq gives one close series
    if "volume" not in df.columns:
        df["volume"] = 0
    return df[COLUMNS]


def fetch_stooq(ticker: str, days: int) -> pd.DataFrame:
    stooq_limiter.acquire()
    try:
        resp = requests.get(
            "https://stooq.com/q/d/l/",
            params={"s": f"{ticker.lower()}.us", "i": "d"},  # US tickers only
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise TransientError(str(e)) from e
    return parse_stooq(resp.text, ticker, days)