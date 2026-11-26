from stock_agent.news import normalize_news


def test_new_nested_shape():
    items = [{"content": {"title": "Big news", "provider": {"displayName": "Reuters"},
                          "pubDate": "2026-11-25T10:00:00Z",
                          "canonicalUrl": {"url": "https://example.com/a"}}}]
    out = normalize_news(items)
    assert out[0]["publisher"] == "Reuters" and out[0]["url"] == "https://example.com/a"


def test_old_flat_shape_and_limit():
    items = [{"title": f"t{i}", "publisher": "X", "providerPublishTime": 1700000000, "link": "u"} for i in range(10)]
    out = normalize_news(items, limit=3)
    assert len(out) == 3 and out[0]["published"].startswith("2023")


def test_skips_items_without_title():
    assert normalize_news([{"content": {}}, {}]) == []