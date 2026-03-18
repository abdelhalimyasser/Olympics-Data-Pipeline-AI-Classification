WITH summer AS (
    SELECT 
        'Summer' AS season,
        games_year,
        host_city,
        host_country,
        number_medal_events AS total_events,  -- << التعديل هنا (وحدنا الاسم)
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        total AS total_medals,
        athlete_with_most_medals,
        athlete_with_most_medals_country,
        athlete_with_most_gold_medals,
        athlete_with_most_gold_medals_country
    FROM {{ ref('stg_summer_sports_medalist_by_olympiad') }}
),

winter AS (
    SELECT 
        'Winter' AS season,
        games_year,
        host_city,
        host_country,
        total_events,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        total AS total_medals,
        athlete_with_most_medals,
        athlete_with_most_medals_country,
        athlete_with_most_gold_medals,
        athlete_with_most_gold_medals_country
    FROM {{ ref('stg_winter_sports_medalist_by_olympiad') }}
)

SELECT * FROM summer
UNION ALL
SELECT * FROM winter
ORDER BY games_year DESC