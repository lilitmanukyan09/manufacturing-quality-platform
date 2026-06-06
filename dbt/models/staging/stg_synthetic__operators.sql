with source as (
    select * from {{ source('raw_synthetic', 'operators') }}
)

select 
    operator_id,
    experience_level,
    hire_date,
    certification_type,
    primary_shift
from source