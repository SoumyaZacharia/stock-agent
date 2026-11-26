import numpy as np
import pandas as pd
import pytest

from stock_agent.indicators import macd, rsi, sma, snapshot, volatility


def test_sma_exact():
    s = pd.Series(range(1, 11), dtype=float)
    assert sma(s, 5).iloc[-1] == 8.0  # mean of 6..10


def test_rsi_all_up_is_100():
    assert rsi(pd.Series(range(1, 40), dtype=float)).iloc[-1] == 100


def test_rsi_all_down_is_0():
    assert rsi(pd.Series(range(40, 1, -1), dtype=float)).iloc[-1] == pytest.approx(0)


def test_rsi_flat_is_50():
    assert rsi(pd.Series([10.0] * 40)).iloc[-1] == 50


def test_rsi_bounds_on_random_walk():
    rng = np.random.default_rng(1)
    s = pd.Series(100 + rng.normal(0, 1, 300).cumsum())
    r = rsi(s).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_macd_constant_is_zero():
    line, sig, hist = macd(pd.Series([50.0] * 60))
    assert line.iloc[-1] == pytest.approx(0)
    assert hist.iloc[-1] == pytest.approx(0)


def test_volatility_constant_is_zero():
    assert volatility(pd.Series([50.0] * 40)).iloc[-1] == pytest.approx(0)


def test_snapshot_full_and_short():
    full = pd.DataFrame({"date": range(300), "close": np.linspace(100, 150, 300)})
    snap = snapshot(full)
    assert snap["rsi14"] == 100 and snap["rsi_state"] == "overbought"
    assert snap["sma200"] is not None and snap["above_sma200"] is True

    short = full.head(30)
    snap = snapshot(short)
    assert snap["sma200"] is None and snap["above_sma200"] is None