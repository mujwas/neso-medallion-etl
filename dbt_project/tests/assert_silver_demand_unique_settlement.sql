select
    settlement_date,
    settlement_period,
    count(*) as n
from {{ ref('silver_demand') }}
group by settlement_date, settlement_period
having count(*) > 1
