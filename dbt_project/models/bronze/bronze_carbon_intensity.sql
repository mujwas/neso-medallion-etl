select
    *,
    current_timestamp as _extracted_at
from {{ source('cic', 'intensity') }}
