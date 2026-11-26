import pytest

from stock_agent.validation import clamp, validate_ticker


def test_ticker_normalized():
    assert validate_ticker(" msft ") == "MSFT"
    assert validate_ticker("brk-b") == "BRK-B"


@pytest.mark.parametrize("bad", ["", "AAPL; DROP TABLE", "../etc", "WAYTOOLONGTICKER", None, 123])
def test_bad_tickers(bad):
    with pytest.raises(ValueError):
        validate_ticker(bad)


def test_clamp():
    assert clamp(9999, 1, 365) == 365
    assert clamp(-5, 1, 365) == 1
    with pytest.raises(ValueError):
        clamp("abc", 1, 365)