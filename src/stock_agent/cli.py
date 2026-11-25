import argparse
import logging

from .service import get_prices


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Fetch and store daily prices")
    p.add_argument("ticker")
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--force", action="store_true", help="skip the cache")
    args = p.parse_args()

    df, source = get_prices(args.ticker, args.days, force=args.force)
    print(f"{len(df)} rows for {args.ticker.upper()} (source: {source})")
    print(df.tail(5)[["date", "close", "volume"]].to_string(index=False))


if __name__ == "__main__":
    main()