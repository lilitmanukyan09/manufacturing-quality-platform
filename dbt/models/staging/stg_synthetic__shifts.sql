with source as (
    select * from {{ source('raw_synthetic', 'shifts') }}
)

select 
    shift_id,
    shift_name,
    shift_date,
    shift_start,
    shift_end,
    supervisor_id
from source