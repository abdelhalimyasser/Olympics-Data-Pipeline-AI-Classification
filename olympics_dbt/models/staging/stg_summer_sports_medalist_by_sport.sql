with raw_data as (
    select * from {{ ref('raw_summer_sports_medalist_by_sport') }}
),

cleaned_data as (
    select
        trim(
            regexp_replace(
                regexp_replace(discipline, '\(.*\)', '', 'g'),
                '\s{2,}', ' ', 'g'
            )
        )                                                    as discipline,

        trim(
            regexp_replace(
                regexp_replace(
                    regexp_replace(contestes, '\[.*?\]', '', 'g'),
                    'Summer:\s*|Winter:\s*', '', 'g'
                ),
                '\s{2,}', ' ', 'g'
            )
        )                                                    as years_contested,
        cast(number_of_olympics      as int)                 as number_of_olympics,
        cast(number_of_medals        as int)                 as number_of_medal_events,
        cast(number_of_gold_medals   as int)                 as number_of_gold_medals,
        cast(number_of_silver_medals as int)                 as number_of_silver_medals,
        cast(number_of_bronze_medals as int)                 as number_of_bronze_medals,

        case
            when athlete_with_most_medals is null
              or trim(athlete_with_most_medals) in ('', 'see list')
            then null
            else trim(replace(athlete_with_most_medals, chr(160), ' '))
        end                                                  as raw_medals_athlete,

        case
            when athlete_with_most_gold_medals is null
              or trim(athlete_with_most_gold_medals) in ('', 'see list')
            then null
            else trim(replace(athlete_with_most_gold_medals, chr(160), ' '))
        end                                                  as raw_gold_athlete

    from raw_data
),

final_model as (
    select
        discipline,
        years_contested,
        number_of_olympics,
        number_of_medal_events,
        number_of_gold_medals,
        number_of_silver_medals,
        number_of_bronze_medals,
        (number_of_gold_medals + number_of_silver_medals + number_of_bronze_medals) as total_medals,

        nullif(trim(regexp_extract(raw_medals_athlete, '^([^\(]+)', 1)), '')         as athlete_with_most_medals,
        regexp_extract(raw_medals_athlete, '\(([A-Z]{2,3}(?:,\s*[A-Z]{2,3})*)\)', 1) as athlete_with_most_medals_country,
        nullif(trim(regexp_extract(raw_gold_athlete, '^([^\(]+)', 1)), '')           as athlete_with_most_gold_medals,
        regexp_extract(raw_gold_athlete, '\(([A-Z]{2,3}(?:,\s*[A-Z]{2,3})*)\)', 1)   as athlete_with_most_gold_medals_country

    from cleaned_data
)

select * from final_model