"""Unit tests for the extractor CLI argument parsing and output paths."""

import datetime as dt

import polars as pl

from src.extract import carbon_intensity, neso_demand


def test_neso_demand_parse_args_with_date():
    args = neso_demand.parse_args(["--date", "2026-01-01"])
    assert args.date == dt.date(2026, 1, 1)


def test_neso_demand_parse_args_default():
    args = neso_demand.parse_args([])
    assert args.date is None


def test_neso_demand_write_parquet_path(tmp_path, monkeypatch):
    monkeypatch.setattr(neso_demand, "OUTPUT_ROOT", tmp_path)
    df = pl.DataFrame({"a": [1, 2]})

    out_path = neso_demand.write_parquet(df, dt.date(2026, 1, 1))

    assert out_path == tmp_path / "2026" / "01" / "01.parquet"
    assert out_path.exists()


def test_carbon_intensity_parse_args_with_date():
    args = carbon_intensity.parse_args(["--date", "2026-01-01"])
    assert args.date == dt.date(2026, 1, 1)


def test_carbon_intensity_parse_args_default():
    args = carbon_intensity.parse_args([])
    assert args.date is None


def test_carbon_intensity_write_parquet_path(tmp_path, monkeypatch):
    monkeypatch.setattr(carbon_intensity, "OUTPUT_ROOT", tmp_path)
    df = pl.DataFrame({"a": [1, 2]})

    out_path = carbon_intensity.write_parquet(df, dt.date(2026, 1, 1))

    assert out_path == tmp_path / "2026" / "01" / "01.parquet"
    assert out_path.exists()
