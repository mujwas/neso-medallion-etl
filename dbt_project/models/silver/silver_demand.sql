{{
    config(
        unique_key=['settlement_date', 'settlement_period'],
        incremental_strategy='merge',
        on_schema_change='sync_all_columns'
    )
}}

select
    cast(SETTLEMENT_DATE as date) as settlement_date,
    cast(SETTLEMENT_PERIOD as integer) as settlement_period,
    cast(ND as double) as nd,
    cast(TSD as double) as tsd,
    cast(ENGLAND_WALES_DEMAND as double) as england_wales_demand,
    cast(EMBEDDED_WIND_GENERATION as double) as embedded_wind_generation,
    cast(EMBEDDED_WIND_CAPACITY as double) as embedded_wind_capacity,
    cast(EMBEDDED_SOLAR_GENERATION as double) as embedded_solar_generation,
    cast(EMBEDDED_SOLAR_CAPACITY as double) as embedded_solar_capacity,
    NON_BM_STOR as non_bm_stor,
    PUMP_STORAGE_PUMPING as pump_storage_pumping,
    SCOTTISH_TRANSFER as scottish_transfer,
    IFA_FLOW as ifa_flow,
    IFA2_FLOW as ifa2_flow,
    BRITNED_FLOW as britned_flow,
    MOYLE_FLOW as moyle_flow,
    EAST_WEST_FLOW as east_west_flow,
    NEMO_FLOW as nemo_flow,
    NSL_FLOW as nsl_flow,
    ELECLINK_FLOW as eleclink_flow,
    VIKING_FLOW as viking_flow,
    GREENLINK_FLOW as greenlink_flow,
    _extracted_at
from {{ ref('bronze_neso_demand') }}
where SETTLEMENT_PERIOD between 1 and 48
qualify row_number() over (
    partition by settlement_date, settlement_period
    order by _extracted_at desc
) = 1
