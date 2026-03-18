WITH raw_data AS (
    SELECT * FROM {{ ref('raw_winter_sports_medalist_by_olympiad') }}
),

cleaned_data AS (
    SELECT
        CAST(games AS INT)                                                                           AS games_year,
        TRIM(split_part(host, ',', 1))                                                               AS host_city,
        TRIM(regexp_replace(
            regexp_extract(trim(host), '.*,\s*(.+)$', 1),
            '\[.*?\]', '', 'g'
        ))                                                                                           AS host_country,
        CAST(regexp_replace(trim(CAST(number_medal_events AS VARCHAR)), '\[.*?\]', '', 'g') AS INT)  AS total_events,
        CAST(number_of_gold_medals AS INT)                                                           AS number_of_gold_medals,
        CAST(number_of_silver_medals AS INT)                                                         AS number_of_silver_medals,
        CAST(number_of_bronze_medals AS INT)                                                         AS number_of_bronze_medals,
        TRIM(replace(athlete_with_most_medals, chr(160), ' '))                                       AS raw_medals_athlete,
        TRIM(replace(athlete_with_most_gold_medals, chr(160), ' '))                                  AS raw_gold_athlete

    FROM raw_data
),

final_model AS (
    SELECT
        games_year,
        host_city,
        host_country,
        total_events,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        (number_of_gold_medals + number_of_silver_medals + number_of_bronze_medals)  AS total,
        TRIM(regexp_extract(raw_medals_athlete, '^([^\(]+)', 1))                     AS athlete_with_most_medals,
        regexp_extract(raw_medals_athlete, '\(([A-Z]{2,3}(?:,\s*[A-Z]{2,3})*)\)', 1) AS athlete_with_most_medals_country,
        TRIM(regexp_extract(raw_gold_athlete, '^([^\(]+)', 1))                       AS athlete_with_most_gold_medals,
        regexp_extract(raw_gold_athlete, '\(([A-Z]{2,3}(?:,\s*[A-Z]{2,3})*)\)', 1)   AS athlete_with_most_gold_medals_country

    FROM cleaned_data
)

SELECT 
    games_year,
    host_city,
    host_country,
    total_events,
    number_of_gold_medals,
    number_of_silver_medals,
    number_of_bronze_medals,
    total,
    athlete_with_most_medals,
    athlete_with_most_medals_country,
    athlete_with_most_gold_medals,
    athlete_with_most_gold_medals_country
FROM final_model
ORDER BY games_year