with source as (
    select * from {{ source('raw', 'ai4i_sensor_readings') }}
)

select
    udi,
    product_id,
    type,
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
    machine_failure::boolean as machine_failure,
    twf::boolean as twf,
    hdf::boolean as hdf,
    pwf::boolean as pwf,
    osf::boolean as osf,
    rnf::boolean as rnf
from source