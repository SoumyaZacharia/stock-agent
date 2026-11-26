import re

TICKER_RE = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,9}$")


def validate_ticker(value) -> str:
    if not isinstance(value, str):
        raise ValueError("ticker must be a string like 'MSFT'")
    t = value.strip().upper()
    if not TICKER_RE.match(t):
        raise ValueError(f"Invalid ticker '{value}'. Use letters, digits, '.' or '-', max 10 chars.")
    return t


def clamp(value, lo: int, hi: int) -> int:
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValueError("expected a whole number") from None
    return max(lo, min(hi, v))