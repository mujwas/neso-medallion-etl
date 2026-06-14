with date_spine as (
    select cast(unnest(generate_series(
        date '2001-01-01', current_date, interval '1 day'
    )) as date) as full_date
)

select
    cast(strftime(full_date, '%Y%m%d') as integer) as date_key,
    full_date,
    cast(date_part('year', full_date) as integer) as year,
    cast(date_part('month', full_date) as integer) as month,
    strftime(full_date, '%B') as month_name,
    cast(date_part('quarter', full_date) as integer) as quarter,
    cast(date_part('isodow', full_date) as integer) as day_of_week,
    strftime(full_date, '%A') as day_name,
    date_part('isodow', full_date) in (6, 7) as is_weekend,
    case
        when date_part('month', full_date) >= 4
            then cast(date_part('year', full_date) as integer)
        else cast(date_part('year', full_date) as integer) - 1
    end as financial_year
from date_spine
