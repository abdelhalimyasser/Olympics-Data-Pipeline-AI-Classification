SELECT 
    'Summer' AS season,
    discipline,
    contest_year,
    number_of_olympics,
    gold_medals,
    silver_medals,
    bronze_medals
FROM {{ ref('stg_discontinued_summer_sports') }}