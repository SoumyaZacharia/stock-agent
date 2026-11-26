import math

import numpy as np
import pandas as pd


def _num(x, digits=4):
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else round(x, digits)


def sma(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_loss != 0, 100.0)               # no losses -> 100
    out = out.where(~((avg_loss == 0) & (avg_gain == 0)), 50.0)  # flat -> 50
    return out.where(avg_gain.notna())


def macd(close: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    line = ema_fast - ema_slow
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return line, sig, line - sig


def volatility(close: pd.Series, window: int = 20) -> pd.Series:
    """Annualized volatility from daily log returns."""
    logret = np.log(close / close.shift(1))
    return logret.rolling(window).std() * math.sqrt(252)


def rsi_state(value):
    if value is None:
        return None
    if value >= 70:
        return "overbought"
    if value <= 30:
        return "oversold"
    return "neutral"


def snapshot(df: pd.DataFrame) -> dict:
    """Latest indicator values for a price frame with 'date' and 'close' columns."""
    if df.empty:
        raise ValueError("no price data")
    close = df["close"].astype(float).reset_index(drop=True)

    macd_line, macd_sig, macd_hist = macd(close)
    r = _num(rsi(close).iloc[-1])
    s20 = _num(sma(close, 20).iloc[-1])
    s50 = _num(sma(close, 50).iloc[-1])
    s200 = _num(sma(close, 200).iloc[-1])
    last_close = _num(close.iloc[-1])
    hist = _num(macd_hist.iloc[-1])

    return {
        "close": last_close,
        "rsi14": r,
        "rsi_state": rsi_state(r),
        "macd": _num(macd_line.iloc[-1]),
        "macd_signal": _num(macd_sig.iloc[-1]),
        "macd_hist": hist,
        "macd_state": None if hist is None else ("bullish" if hist > 0 else "bearish" if hist < 0 else "neutral"),
        "sma20": s20,
        "sma50": s50,
        "sma200": s200,
        "above_sma50": None if s50 is None else last_close > s50,
        "above_sma200": None if s200 is None else last_close > s200,
        "volatility_20d_annualized": _num(volatility(close).iloc[-1]),
        "rows_used": int(len(close)),
    }