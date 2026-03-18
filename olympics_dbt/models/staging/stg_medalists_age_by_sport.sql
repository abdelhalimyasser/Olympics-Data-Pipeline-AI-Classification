WITH source_data AS (
    SELECT * FROM {{ ref('raw_medalists_age_by_sport') }}
),

cleaned_data AS (
    SELECT 
        TRIM(sport)                                    AS sport,
        TRIM(title)                                    AS title,
        CAST(REGEXP_EXTRACT(age, '(\d+)') AS INTEGER) AS age_years,
        
        CASE 
            WHEN age LIKE '%days%' 
            THEN CAST(REGEXP_EXTRACT(age, '(\d+)\s+days', 1) AS DOUBLE) / 365.25
            ELSE 0 
        END AS age_days_fraction,

        TRIM(medalist)                                 AS medalist,
        TRIM(details)                                  AS details
    FROM source_data
)

SELECT 
    medalist,
    ROUND(age_years + age_days_fraction, 2) AS age,
    sport,
    title,
    details
FROM cleaned_data
