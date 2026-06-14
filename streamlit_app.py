"""GB carbon intensity & demand dashboard, reading from the DuckDB warehouse."""

from pathlib import Path

import duckdb
import plotly.express as px
import polars as pl
import streamlit as st

DB_PATH = Path("data/warehouse.duckdb")

st.set_page_config(page_title="NESO Carbon & Demand Dashboard", layout="wide")

if not DB_PATH.exists():
    st.error(
        "No warehouse found at `data/warehouse.duckdb`. Run:\n\n"
        "`uv run dbt build --project-dir dbt_project --profiles-dir dbt_project --target dev`"
    )
    st.stop()


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH), read_only=True)


def query(sql: str, params: list | None = None) -> pl.DataFrame:
    return get_connection().execute(sql, params or []).pl()


st.title("GB Carbon Intensity & Demand")

with st.sidebar:
    st.header("About")
    last_updated = query(
        """
        select greatest(
            (select max(_extracted_at) from silver_demand),
            (select max(_extracted_at) from silver_carbon_intensity)
        ) as last_updated
        """
    )["last_updated"][0]
    st.metric("Data last updated", str(last_updated))
    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown(
        "- [NESO Data Portal](https://www.neso.energy/data-portal) "
        "— GB half-hourly demand\n"
        "- [Carbon Intensity API](https://carbonintensity.org.uk/) "
        "— GB carbon intensity forecasts and actuals"
    )

st.header("GB Carbon Intensity")

carbon = query(
    """
    select full_date, avg_forecast_gco2_per_kwh, avg_actual_gco2_per_kwh
    from agg_daily_carbon
    order by full_date
    """
)

min_date, max_date = carbon["full_date"].min(), carbon["full_date"].max()
date_range = st.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    carbon = carbon.filter(
        (pl.col("full_date") >= start) & (pl.col("full_date") <= end)
    )

carbon_long = carbon.unpivot(
    index="full_date",
    on=["avg_forecast_gco2_per_kwh", "avg_actual_gco2_per_kwh"],
    variable_name="series",
    value_name="gco2_per_kwh",
)
fig_carbon = px.line(
    carbon_long,
    x="full_date",
    y="gco2_per_kwh",
    color="series",
    labels={"full_date": "Date", "gco2_per_kwh": "gCO2/kWh", "series": "Series"},
)
st.plotly_chart(fig_carbon, width="stretch")

st.header("Half-hourly Demand")

demand_dates = query(
    "select distinct settlement_date from fct_demand_halfhourly order by settlement_date"
)["settlement_date"].to_list()

selected_date = st.selectbox("Settlement date", options=demand_dates, index=len(demand_dates) - 1)

demand = query(
    """
    select settlement_period, nd
    from fct_demand_halfhourly
    where settlement_date = ?
    order by settlement_period
    """,
    [selected_date],
)
demand = demand.with_columns(
    (
        ((pl.col("settlement_period") - 1) // 2).cast(pl.Utf8).str.zfill(2)
        + ":"
        + (((pl.col("settlement_period") - 1) % 2) * 30).cast(pl.Utf8).str.zfill(2)
    ).alias("time")
)
fig_demand = px.line(
    demand,
    x="time",
    y="nd",
    labels={"time": "Time", "nd": "National Demand (MW)"},
)
st.plotly_chart(fig_demand, width="stretch")
