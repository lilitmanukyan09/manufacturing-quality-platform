with source as (
    select * from {{ source('raw_synthetic', 'machines') }}
)

select 
    machine_id,
    machine_type,
    manufacturer,
    installation_date,
    rated_tool_life_min,
    location_in_plant,
    is_active
from source