with source as (
    select * from {{ source('raw_synthetic', 'maintenance_log') }}
)

select 
    maintenance_id,
    machine_id,
    udi,
    maintenance_date,
    maintenance_type,
    tool_replaced_flag,
    duration_min
from source