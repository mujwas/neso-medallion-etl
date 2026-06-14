# Project: NESO Medallion ETL

## Stack
- Python 3.12, managed by uv
- DuckDB embedded warehouse (data/warehouse.duckdb)
- dbt-core 1.9 with dbt-duckdb adapter
- Polars for all dataframe work — no pandas

## Commands
- `uv sync` — install/sync dependencies
- `uv run python -m src.extract.neso_demand` — run demand extractor
- `uv run python -m src.extract.carbon_intensity` — run carbon extractor
- `uv run dbt build --project-dir dbt_project --profiles-dir dbt_project --target dev` — full build + tests
- `uv run dbt docs generate --project-dir dbt_project --profiles-dir dbt_project && uv run dbt docs serve --project-dir dbt_project` — docs
- `uv run streamlit run streamlit_app.py` — dashboard
- `uv run pytest tests/` — run extractor unit tests

## Conventions
- UK English spelling throughout
- Bronze = views over raw Parquet; never materialise
- Silver = incremental tables; deduplicate on (settlement_date, period)
- Gold = tables; star schema only
- All dbt transformations in SQL — no Python models
- Tests mandatory on every silver and gold model

## Off-limits
- Do not edit or create files under data/raw/**
- Do not commit .env or data/warehouse.duckdb
- Do not introduce pandas anywhere