WITH source_data AS (
    SELECT * FROM {{ ref('raw_discontinued_summer_sports') }}
),

standardized_years AS (
    SELECT 
        discipline,
        REPLACE(REPLACE(REPLACE(contestes, '–', ','), '; ', ','), ';', ',') AS years_cleaned,
        number_of_olympics,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals
    FROM source_data
),

final_cleaned AS (
    SELECT 
        TRIM(discipline)                                 AS discipline,
        CAST(TRIM(CAST(year_val AS VARCHAR)) AS INTEGER) AS contest_year,
        CAST(number_of_olympics AS INTEGER)              AS number_of_olympics,
        CAST(number_of_gold_medals AS INTEGER)           AS gold_medals,
        CAST(number_of_silver_medals AS INTEGER)         AS silver_medals,
        CAST(number_of_bronze_medals AS INTEGER)         AS bronze_medals
    FROM standardized_years,
    UNNEST(SPLIT(years_cleaned, ',')) AS t(year_val)
)

SELECT * FROM final_cleaned