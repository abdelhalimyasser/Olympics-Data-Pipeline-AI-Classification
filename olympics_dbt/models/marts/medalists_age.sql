SELECT 
    medalist,
    age,
    sport,
    title,
    details
FROM {{ ref('stg_medalists_age_by_sport') }}