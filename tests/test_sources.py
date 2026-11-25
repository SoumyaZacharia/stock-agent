import pytest

from stock_agent import sources


def test_parse_stooq_ok():
    text = "Date,Open,High,Low,Close,Volume\n2099-01-01,1,2,0.5,1.5,100\n"
    # future date is always inside the window, so this test never goes stale
    df = sources.parse_stooq(text, "AAPL", days=36500)
    assert len(df) == 1
    assert df["adj_close"].iloc[0] == 1.5


def test_parse_stooq_no_data():
    with pytest.raises(ValueError):
        sources.parse_stooq("No data", "AAPL", 30)


def test_yahoo_retries_then_succeeds(monkeypatch, sample_df):
    calls = {"n": 0}

    def flaky(ticker, days):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("rate limited")
        return sample_df

    class NoLimit:
        def acquire(self):
            pass

    monkeypatch.setattr(sources, "fetch_prices", flaky)
    monkeypatch.setattr(sources, "yahoo_limiter", NoLimit())
    monkeypatch.setattr(sources.fetch_yahoo.retry, "sleep", lambda s: None)

    sources.fetch_yahoo("AAPL", 30)
    assert calls["n"] == 3