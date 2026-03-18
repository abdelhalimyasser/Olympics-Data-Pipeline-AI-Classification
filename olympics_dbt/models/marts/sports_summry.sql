WITH summer AS (
    SELECT 
        'Summer' AS season,
        discipline,
        number_of_olympics,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        total_medals,
        athlete_with_most_medals,
        athlete_with_most_gold_medals
    FROM {{ ref('stg_summer_sports_medalist_by_sport') }}
),

winter AS (
    SELECT 
        'Winter' AS season,
        discipline,
        number_of_olympics,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        total_medals,
        athlete_with_most_medals,
        athlete_with_most_gold_medals
    FROM {{ ref('stg_winter_sports_medalist_by_sport') }}
)

SELECT * FROM summer
UNION ALL
SELECT * FROM winter