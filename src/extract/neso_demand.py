"""Extract half-hourly GB demand data from the NESO Data Portal to raw Parquet."""

import argparse
import datetime as dt
import json
import logging
import sys
from pathlib import Path

import polars as pl
import requests

API_URL = "https://api.neso.energy/api/3/action/datastore_search"

# "Historic Demand Data" is published as one resource per calendar year.
RESOURCE_IDS: dict[int, str] = {
    2001: "e8608e9a-f56c-457f-b9e7-bfffcfd19731",
    2002: "4daaac31-ae56-461e-8efe-6b33e147225a",
    2003: "30650247-acbf-414d-8ae2-2aa4aac57537",
    2004: "5f5c076c-d3a3-4f33-a137-501cc3d2ca9b",
    2005: "42a41acd-53b6-450d-af1b-4a92a352895c",
    2006: "949bb4a4-8374-4730-89ef-302d82428d2c",
    2007: "c0da767c-447d-48d1-93fd-ca3955d078ae",
    2008: "ec63adc8-e8a1-45cc-a593-5953b1ede7b1",
    2009: "ed8a37cb-65ac-4581-8dbc-a3130780da3a",
    2010: "b3eae4a5-8c3c-4df1-b9de-7db243ac3a09",
    2011: "01522076-2691-4140-bfb8-c62284752efd",
    2012: "4bf713a2-ea0c-44d3-a09a-63fc6a634b00",
    2013: "2ff7aaff-8b42-4c1b-b234-9446573a1e27",
    2014: "b9005225-49d3-40d1-921c-03ee2d83a2ff",
    2015: "cc505e45-65ae-4819-9b90-1fbb06880293",
    2016: "3bb75a28-ab44-4a0b-9b1c-9be9715d3c44",
    2017: "2f0f75b8-39c5-46ff-a914-ae38088ed022",
    2018: "fcb12133-0db0-4f27-a4a5-1669fd9f6d33",
    2019: "dd9de980-d724-415a-b344-d8ae11321432",
    2020: "33ba6857-2a55-479f-9308-e5c4c53d4381",
    2021: "18c69c42-f20d-46f0-84e9-e279045befc6",
    2022: "bb44a1b5-75b1-4db2-8491-257f23385006",
    2023: "bf5ab335-9b40-4ea4-b93a-ab4af7bce003",
    2024: "f6d02c0f-957b-48cb-82ee-09003f2ba759",
    2025: "b2bde559-3455-4021-b179-dfe60c0337b0",
    2026: "8a4a771c-3929-4e56-93ad-cdf13219dea5",
}

OUTPUT_ROOT = Path("data/raw/neso/demand")

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_demand(target_date: dt.date) -> pl.DataFrame:
    """Fetch half-hourly demand records for a single settlement date."""
    try:
        resource_id = RESOURCE_IDS[target_date.year]
    except KeyError:
        raise ValueError(
            f"No known NESO resource_id for year {target_date.year}"
        ) from None

    params = {
        "resource_id": resource_id,
        "filters": json.dumps({"SETTLEMENT_DATE": target_date.isoformat()}),
        "limit": 100,
    }

    logger.info(
        "Requesting NESO demand data for %s (resource_id=%s)",
        target_date.isoformat(),
        resource_id,
    )
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch NESO demand data for %s", target_date.isoformat())
        raise

    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"NESO API returned an error: {payload}")

    records = payload["result"]["records"]
    logger.info("Fetched %d records for %s", len(records), target_date.isoformat())
    return pl.DataFrame(records)


def write_parquet(df: pl.DataFrame, target_date: dt.date) -> Path:
    """Write a day's demand data to data/raw/neso/demand/{yyyy}/{mm}/{dd}.parquet."""
    out_dir = OUTPUT_ROOT / f"{target_date:%Y}" / f"{target_date:%m}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{target_date:%d}.parquet"
    df.write_parquet(out_path)
    logger.info("Wrote %d rows to %s", df.height, out_path)
    return out_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract NESO half-hourly demand data to Parquet")
    parser.add_argument(
        "--date",
        type=dt.date.fromisoformat,
        default=None,
        help="Settlement date to extract (YYYY-MM-DD); defaults to yesterday",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target_date = args.date or dt.date.today() - dt.timedelta(days=1)

    try:
        df = fetch_demand(target_date)
    except (requests.RequestException, RuntimeError, ValueError):
        logger.error("Extraction failed for %s", target_date.isoformat())
        return 1

    if df.is_empty():
        logger.warning("No records returned for %s; nothing written", target_date.isoformat())
        return 0

    write_parquet(df, target_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
