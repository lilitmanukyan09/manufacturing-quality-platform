with source as (
    select * from {{ source('raw', 'operator_assignments') }}
)

select
    udi,
    operator_id,
    machine_id
from source