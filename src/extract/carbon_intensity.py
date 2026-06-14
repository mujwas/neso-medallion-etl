"""Extract half-hourly GB carbon intensity data from the Carbon Intensity API to raw Parquet."""

import argparse
import datetime as dt
import logging
import sys
from pathlib import Path

import polars as pl
import requests

API_URL = "https://api.carbonintensity.org.uk/intensity/date"

OUTPUT_ROOT = Path("data/raw/cic/intensity")

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_intensity(target_date: dt.date) -> pl.DataFrame:
    """Fetch half-hourly carbon intensity records for a single date."""
    url = f"{API_URL}/{target_date.isoformat()}"

    logger.info("Requesting carbon intensity data for %s", target_date.isoformat())
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch carbon intensity data for %s", target_date.isoformat())
        raise

    payload = response.json()
    if "data" not in payload:
        raise RuntimeError(f"Carbon Intensity API returned an error: {payload}")

    records = payload["data"]
    logger.info("Fetched %d records for %s", len(records), target_date.isoformat())
    return pl.DataFrame(records)


def write_parquet(df: pl.DataFrame, target_date: dt.date) -> Path:
    """Write a day's carbon intensity data to data/raw/cic/intensity/{yyyy}/{mm}/{dd}.parquet."""
    out_dir = OUTPUT_ROOT / f"{target_date:%Y}" / f"{target_date:%m}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{target_date:%d}.parquet"
    df.write_parquet(out_path)
    logger.info("Wrote %d rows to %s", df.height, out_path)
    return out_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract GB carbon intensity data to Parquet")
    parser.add_argument(
        "--date",
        type=dt.date.fromisoformat,
        default=None,
        help="Date to extract (YYYY-MM-DD); defaults to yesterday",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target_date = args.date or dt.date.today() - dt.timedelta(days=1)

    try:
        df = fetch_intensity(target_date)
    except (requests.RequestException, RuntimeError):
        logger.error("Extraction failed for %s", target_date.isoformat())
        return 1

    if df.is_empty():
        logger.warning("No records returned for %s; nothing written", target_date.isoformat())
        return 0

    write_parquet(df, target_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
