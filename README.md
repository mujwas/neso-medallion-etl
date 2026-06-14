# NESO Medallion ETL

[![CI](https://github.com/mujwas/neso-medallion-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/mujwas/neso-medallion-etl/actions/workflows/ci.yml)

## Overview

A local medallion ELT pipeline built on public UK National Grid data — GB
electricity demand and carbon intensity. Built as a portfolio project to
demonstrate a modern, lightweight data stack: dbt for transformation, DuckDB
as an embedded warehouse, Polars for dataframe work, and Streamlit for
visualisation.

## Architecture

Raw data flows through three layers (bronze → silver → gold) before being
visualised in a Streamlit dashboard:

- **Bronze** (`dbt_project/models/bronze/`) — views over raw Parquet files,
  never materialised: `bronze_neso_demand`, `bronze_carbon_intensity`
- **Silver** (`dbt_project/models/silver/`) — incremental tables, typed and
  deduplicated on settlement date/period or timestamp: `silver_demand`,
  `silver_carbon_intensity`
- **Gold** (`dbt_project/models/gold/`) — star schema, table materialisation:
  `dim_date`, `fct_demand_halfhourly`, `agg_daily_carbon`
- **Dashboard** (`streamlit_app.py`) — reads the gold layer from
  `data/warehouse.duckdb` via DuckDB and Polars, charted with Plotly

## Stack

- Python 3.12, managed by [uv](https://docs.astral.sh/uv/)
- [Polars](https://pola.rs/) for all dataframe work
- [DuckDB](https://duckdb.org/) as an embedded warehouse
- [dbt-core](https://docs.getdbt.com/) 1.11 with the dbt-duckdb adapter
- [Streamlit](https://streamlit.io/) for the dashboard
- GitHub Actions for CI

## Quickstart

```sh
uv sync
uv run python -m src.extract.neso_demand && uv run python -m src.extract.carbon_intensity
uv run dbt build --project-dir dbt_project --profiles-dir dbt_project --target dev
uv run streamlit run streamlit_app.py
```

The extractors default to yesterday's date; pass `--date YYYY-MM-DD` to
extract a specific day.

## Data sources

- [NESO Data Portal](https://www.neso.energy/data-portal) — historic GB
  half-hourly demand
- [Carbon Intensity API](https://carbonintensity.org.uk/) — GB carbon
  intensity forecasts and actuals

Both APIs are public and require no API key or secrets.

## Testing & CI

The dbt project has 83 tests across the silver and gold layers (`not_null`,
`unique`, `accepted_values`, `relationships`, plus a singular test for
composite-key uniqueness), bringing `dbt build` to 90 total nodes. CI runs
the full extract → build → test → pytest sequence on every push and pull
request to `master`.

> **Note:** the dashboard reads `data/warehouse.duckdb`, which is gitignored
> and not shipped in the repo — run the quickstart steps above (through
> `dbt build`) locally before launching Streamlit. The CI badge reflects the
> health of the pipeline itself, not the dashboard.

## Development

Built with [Claude Code](https://claude.ai/code) as the AI-native development
environment — used for API exploration, code generation, dbt model scaffolding,
and test authorship. All generated code reviewed and verified against live APIs
and real data.
