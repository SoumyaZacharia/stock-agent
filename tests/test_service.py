import pytest

from stock_agent import service
from stock_agent.circuit import CircuitBreaker
from stock_agent.db import get_conn
from stock_agent.sources import TransientError


@pytest.fixture
def conn(tmp_path):
    return get_conn(tmp_path / "t.db")


@pytest.fixture(autouse=True)
def fresh_breaker(monkeypatch):
    monkeypatch.setattr(service, "yahoo_breaker", CircuitBreaker(failure_threshold=2, reset_after=300))


def test_yahoo_then_cache(monkeypatch, conn, sample_df):
    calls = {"n": 0}

    def fake_yahoo(t, d):
        calls["n"] += 1
        return sample_df

    monkeypatch.setattr(service, "fetch_yahoo", fake_yahoo)
    df, src = service.get_prices("AAPL", 30, conn=conn)
    assert src == "yahoo" and len(df) == 2
    df, src = service.get_prices("AAPL", 30, conn=conn)
    assert src == "cache" and calls["n"] == 1


def test_falls_back_to_stooq(monkeypatch, conn, sample_df):
    def boom(t, d):
        raise TransientError("429")

    monkeypatch.setattr(service, "fetch_yahoo", boom)
    monkeypatch.setattr(service, "fetch_stooq", lambda t, d: sample_df)
    _, src = service.get_prices("AAPL", 30, conn=conn)
    assert src == "stooq"


def test_breaker_skips_yahoo_after_failures(monkeypatch, conn, sample_df):
    calls = {"n": 0}

    def boom(t, d):
        calls["n"] += 1
        raise TransientError("down")

    monkeypatch.setattr(service, "fetch_yahoo", boom)
    monkeypatch.setattr(service, "fetch_stooq", lambda t, d: sample_df)
    for _ in range(3):
        service.get_prices("AAPL", 30, conn=conn, force=True)
    assert calls["n"] == 2  # third call skipped Yahoo entirely


def test_all_sources_fail(monkeypatch, conn):
    def boom(t, d):
        raise TransientError("down")

    def no_data(t, d):
        raise ValueError("no data")

    monkeypatch.setattr(service, "fetch_yahoo", boom)
    monkeypatch.setattr(service, "fetch_stooq", no_data)
    with pytest.raises(service.DataUnavailable):
        service.get_prices("AAPL", 30, conn=conn)