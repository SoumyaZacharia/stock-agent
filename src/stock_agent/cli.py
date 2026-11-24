import argparse
from .db import get_conn
from .prices import fetch_prices, save_prices

def main():
    p = argparse.ArgumentParser(description="Fetch and store daily prices")
    p.add_argument("ticker")
    p.add_argument("--days", type=int, default=365)
    args = p.parse_args()

    df = fetch_prices(args.ticker, args.days)
    conn = get_conn()
    n = save_prices(conn, df)
    print(f"Stored {n} rows for {args.ticker.upper()}")

    rows = conn.execute(
        "SELECT date, close, volume FROM prices WHERE ticker=? "
        "ORDER BY date DESC LIMIT 5", (args.ticker.upper(),)
    ).fetchall()
    for r in rows:
        print(r)

if __name__ == "__main__":
    main()