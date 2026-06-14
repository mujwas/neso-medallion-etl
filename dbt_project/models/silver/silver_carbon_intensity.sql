{{
    config(
        unique_key='from_ts',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns'
    )
}}

select
    strptime("from", '%Y-%m-%dT%H:%MZ') as from_ts,
    strptime("to", '%Y-%m-%dT%H:%MZ') as to_ts,
    intensity.forecast as forecast_gco2_per_kwh,
    intensity.actual as actual_gco2_per_kwh,
    intensity.index as "index",
    _extracted_at
from {{ ref('bronze_carbon_intensity') }}
where intensity.actual is not null
