import numpy as np
import pandas as pd
import pytest

from stock_agent import tools
from stock_agent.service import DataUnavailable


def make_df(n=300):
    close = np.linspace(100, 150, n)
    return pd.DataFrame({
        "ticker": "MSFT", "date": [f"2026-01-{i:04d}" for i in range(n)],
        "open": close, "high": close, "low": close, "close": close,
        "adj_close": close, "volume": 1000,
    })


@pytest.fixture
def stub(monkeypatch):
    seen = {}

    def fake(ticker, days):
        seen["args"] = (ticker, days)
        return make_df(), "cache"

    monkeypatch.setattr(tools, "fetch_history", fake)
    return seen


def test_get_prices_caps_days_and_rows(stub):
    out = tools.get_prices("msft", days=99999)
    assert stub["args"] == ("MSFT", 365)
    assert out["count"] == 90 and out["truncated"] is True


def test_get_prices_rejects_bad_ticker(stub):
    with pytest.raises(ValueError):
        tools.get_prices("MSFT; rm -rf")


def test_get_indicators(stub):
    out = tools.get_indicators("MSFT")
    assert out["indicators"]["rsi14"] == 100
    assert stub["args"][1] == tools.INDICATOR_LOOKBACK_DAYS


def test_unavailable_becomes_clean_error(monkeypatch):
    def boom(t, d):
        raise DataUnavailable("x")

    monkeypatch.setattr(tools, "fetch_history", boom)
    with pytest.raises(RuntimeError, match="temporarily unavailable"):
        tools.get_indicators("MSFT")


def test_get_news_caps_limit(monkeypatch):
    seen = {}
    monkeypatch.setattr(tools, "fetch_news", lambda t, n: seen.setdefault("n", n) and [])
    tools.get_news("MSFT", limit=500)
    assert seen["n"] == 10