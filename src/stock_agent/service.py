import logging
from datetime import date, datetime, timedelta, timezone

import pandas as pd

from .circuit import CircuitBreaker
from .db import get_conn
from .prices import save_prices
from .sources import TransientError, fetch_stooq, fetch_yahoo

log = logging.getLogger(__name__)

yahoo_breaker = CircuitBreaker(failure_threshold=3, reset_after=300)


class DataUnavailable(Exception):
    pass


def is_fresh(conn, ticker: str, days: int, ttl_hours: float) -> bool:
    row = conn.execute(
        "SELECT fetched_at, days FROM fetch_log WHERE ticker=?", (ticker,)
    ).fetchone()
    if not row or row[1] < days:  # cached range is too short
        return False
    age = datetime.now(timezone.utc) - datetime.fromisoformat(row[0])
    return age < timedelta(hours=ttl_hours)


def mark_fetched(conn, ticker: str, source: str, days: int):
    conn.execute(
        "INSERT OR REPLACE INTO fetch_log VALUES (?,?,?,?)",
        (ticker, datetime.now(timezone.utc).isoformat(), source, days),
    )
    conn.commit()


def _fetch_with_fallback(ticker: str, days: int):
    if yahoo_breaker.allow():
        try:
            df = fetch_yahoo(ticker, days)
            yahoo_breaker.record_success()
            return df, "yahoo"
        except TransientError as e:
            yahoo_breaker.record_failure()
            log.warning("Yahoo failed for %s (%s); trying Stooq", ticker, e)
        except ValueError as e:
            log.warning("Yahoo gave no data for %s (%s); trying Stooq", ticker, e)
    else:
        log.warning("Yahoo circuit open; going straight to Stooq")

    try:
        return fetch_stooq(ticker, days), "stooq"
    except Exception as e:
        raise DataUnavailable(f"All sources failed for {ticker}: {e}") from e


def get_prices(ticker: str, days: int = 365, conn=None, ttl_hours: float = 6, force: bool = False):
    """Returns (DataFrame, source) where source is cache, yahoo or stooq."""
    ticker = ticker.upper().strip()
    conn = conn or get_conn()

    if not force and is_fresh(conn, ticker, days, ttl_hours):
        source = "cache"
    else:
        df, source = _fetch_with_fallback(ticker, days)
        save_prices(conn, df)
        mark_fetched(conn, ticker, source, days)

    start = (date.today() - timedelta(days=days)).isoformat()
    out = pd.read_sql(
        "SELECT * FROM prices WHERE ticker=? AND date>=? ORDER BY date",
        conn,
        params=(ticker, start),
    )
    return out, source