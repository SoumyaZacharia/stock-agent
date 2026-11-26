from datetime import datetime, timezone

import yfinance as yf

from .sources import yahoo_limiter


def _iso(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return value


def normalize_news(items, limit: int = 5) -> list[dict]:
    out = []
    for item in items or []:
        c = item.get("content", item)
        title = c.get("title")
        if not title:
            continue
        provider = c.get("provider") or {}
        link = c.get("canonicalUrl") or {}
        out.append(
            {
                "title": str(title)[:200],
                "publisher": provider.get("displayName") or c.get("publisher"),
                "published": _iso(c.get("pubDate") or c.get("providerPublishTime")),
                "url": link.get("url") or c.get("link"),
            }
        )
        if len(out) >= limit:
            break
    return out


def fetch_news(ticker: str, limit: int = 5) -> list[dict]:
    yahoo_limiter.acquire()
    return normalize_news(yf.Ticker(ticker).news, limit)