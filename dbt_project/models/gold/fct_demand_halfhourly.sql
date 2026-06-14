select
    d.date_key,
    s.settlement_date,
    s.settlement_period,
    s.nd,
    s.tsd,
    s.england_wales_demand,
    s.embedded_wind_generation,
    s.embedded_wind_capacity,
    s.embedded_solar_generation,
    s.embedded_solar_capacity,
    s.non_bm_stor,
    s.pump_storage_pumping,
    s.scottish_transfer,
    s.ifa_flow,
    s.ifa2_flow,
    s.britned_flow,
    s.moyle_flow,
    s.east_west_flow,
    s.nemo_flow,
    s.nsl_flow,
    s.eleclink_flow,
    s.viking_flow,
    s.greenlink_flow
from {{ ref('silver_demand') }} as s
inner join {{ ref('dim_date') }} as d
    on s.settlement_date = d.full_date
