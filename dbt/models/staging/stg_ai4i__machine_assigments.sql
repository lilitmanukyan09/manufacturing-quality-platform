with source as (
    select * from {{ source('raw', 'machine_assignments') }}
)

select
    udi,
    machine_id,
    tool_wear,
    is_reset_point,
    tool_life_number
from source