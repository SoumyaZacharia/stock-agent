import pandas as pd
import pytest
from stock_agent.db import get_conn
from stock_agent.prices import normalize, save_prices

def fake_raw():
    idx = pd.to_datetime(["2026-11-20", "2026-11-21"]).tz_localize("America/New_York")
    return pd.DataFrame({
        "Open": [1.0, 2.0], "High": [1.5, 2.5], "Low": [0.9, 1.9],
        "Close": [1.2, 2.2], "Adj Close": [1.2, 2.2], "Volume": [100, 200],
    }, index=pd.Index(idx, name="Date"))

def test_normalize_shape():
    df = normalize(fake_raw(), "AAPL")
    assert list(df.columns) == ["ticker","date","open","high","low","close","adj_close","volume"]
    assert df["date"].iloc[0] == "2026-11-20"

def test_empty_raises():
    with pytest.raises(ValueError):
        normalize(pd.DataFrame(), "XXXX")

def test_save_is_idempotent(tmp_path):
    conn = get_conn(tmp_path / "t.db")
    df = normalize(fake_raw(), "AAPL")
    save_prices(conn, df)
    save_prices(conn, df)  # run twice
    count = conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
    assert count == 2