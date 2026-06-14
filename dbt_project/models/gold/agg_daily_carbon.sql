select
    d.date_key,
    d.full_date,
    avg(c.forecast_gco2_per_kwh) as avg_forecast_gco2_per_kwh,
    min(c.forecast_gco2_per_kwh) as min_forecast_gco2_per_kwh,
    max(c.forecast_gco2_per_kwh) as max_forecast_gco2_per_kwh,
    avg(c.actual_gco2_per_kwh) as avg_actual_gco2_per_kwh,
    min(c.actual_gco2_per_kwh) as min_actual_gco2_per_kwh,
    max(c.actual_gco2_per_kwh) as max_actual_gco2_per_kwh,
    mode(c."index") as carbon_index
from {{ ref('silver_carbon_intensity') }} as c
inner join {{ ref('dim_date') }} as d
    on cast(c.from_ts as date) = d.full_date
group by d.date_key, d.full_date
