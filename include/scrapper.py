import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


def scrapper():
    url = "https://en.wikipedia.org/wiki/Lists_of_Olympic_medalists"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    response = requests.get(url, headers=headers)

    # ===================================================================
    # get all the data in a soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # get all the tabels
    found_table = soup.find_all(
        'table',
        {
            'class':'wikitable'
        }
    )

    # ===================================================================
    # get summer olympic sports
    summer_olympic_sports = found_table[0]

    summer_olympic_sports_data = []

    rows = summer_olympic_sports.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 9:
            summer_sports_medalist_by_sport = {
                'discipline':                    cells[0].text.strip(),
                'contestes':                     cells[1].text.strip(),
                'number_of_olympics':            cells[2].text.strip(),
                'number_of_medals':              cells[3].text.strip(),
                'number_of_gold_medals':         cells[4].text.strip(),
                'number_of_silver_medals':       cells[5].text.strip(),
                'number_of_bronze_medals':       cells[6].text.strip(),
                'total':                         cells[7].text.strip(),
                'athlete_with_most_medals':      cells[8].text.strip(),
                'athlete_with_most_gold_medals': cells[9].text.strip()
            }

            summer_olympic_sports_data.append(summer_sports_medalist_by_sport)

    # ===================================================================
    # get winter olympic sports
    winter_olympic_sports = found_table[1]

    winter_olympic_sports_data = []

    rows = winter_olympic_sports.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 9:
            winter_sports_medalist_by_sport = {
                'discipline':                    cells[0].text.strip(),
                'contestes':                     cells[1].text.strip(),
                'number_of_olympics':            cells[2].text.strip(),
                'number_of_medals':              cells[3].text.strip(),
                'number_of_gold_medals':         cells[4].text.strip(),
                'number_of_silver_medals':       cells[5].text.strip(),
                'number_of_bronze_medals':       cells[6].text.strip(),
                'total':                         cells[7].text.strip(),
                'athlete_with_most_medals':      cells[8].text.strip(),
                'athlete_with_most_gold_medals': cells[9].text.strip()
            }

            winter_olympic_sports_data.append(winter_sports_medalist_by_sport)

    # ===================================================================
    # get discontiued summer sports
    discontinued_summer_sports = found_table[2]

    discontinued_summer_sports_data = []

    rows = discontinued_summer_sports.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 6:
          discontinued_summer_sports = {
                'discipline':                    cells[0].text.strip(),
                'contestes':                     cells[1].text.strip(),
                'number_of_olympics':            cells[2].text.strip(),
                'number_of_gold_medals':         cells[3].text.strip(),
                'number_of_silver_medals':       cells[4].text.strip(),
                'number_of_bronze_medals':       cells[5].text.strip(),
                'total':                         cells[6].text.strip()
                }

          discontinued_summer_sports_data.append(discontinued_summer_sports)

    # ===================================================================
    # get summer olympic olympiad
    summer_olympiad = found_table[3]

    summer_olympiad_data = []

    rows = summer_olympiad.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 11:
           summer_sports_medalist_by_olympiad = {
               'games':                         cells[0].text.strip(),
               'medal_winners':                 cells[1].text.strip(),
               'medal_table':                   cells[2].text.strip(),
               'host':                          cells[3].text.strip(),
               'number_medal_events':           cells[4].text.strip(),
               'number_of_gold_medals':         cells[5].text.strip(),
               'number_of_silver_medals':       cells[6].text.strip(),
               'number_of_bronze_medals':       cells[7].text.strip(),
               'total':                         cells[8].text.strip(),
               'athlete_with_most_medals':      cells[9].text.strip(),
               'athlete_with_most_gold_medals': cells[10].text.strip()
           }

           summer_olympiad_data.append(summer_sports_medalist_by_olympiad)

    # ===================================================================
    # get winter olympic olympiad
    winter_olympiad = found_table[4]

    winter_olympiad_data = []

    rows = winter_olympiad.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 11:
           winter_sports_medalist_by_olympiad = {
               'games':                         cells[0].text.strip(),
               'medal_winners':                 cells[1].text.strip(),
               'medal_table':                   cells[2].text.strip(),
               'host':                          cells[3].text.strip(),
               'number_medal_events':           cells[4].text.strip(),
               'number_of_gold_medals':         cells[5].text.strip(),
               'number_of_silver_medals':       cells[6].text.strip(),
               'number_of_bronze_medals':       cells[7].text.strip(),
               'total':                         cells[8].text.strip(),
               'athlete_with_most_medals':      cells[9].text.strip(),
               'athlete_with_most_gold_medals': cells[10].text.strip()
           }

           winter_olympiad_data.append(winter_sports_medalist_by_olympiad)

    # ===================================================================
    # get medalists age by sport
    medalists_age_by_sport = found_table[5]

    medalists_age_by_sport_data = []
    current_sport = ""

    rows = medalists_age_by_sport.find_all('tr')

    for row in rows:
        sport_header = row.find('th', colspan="5")
        if sport_header:
            current_sport = sport_header.get_text(strip=True)
            continue

        cells = row.find_all('td')
        if len(cells) >= 4:
           row_data = {
               'sport':    current_sport,
               'title':    cells[0].get_text(separator=' ', strip=True),
               'age':      cells[1].get_text(separator=' ', strip=True),
               'medalist': cells[2].get_text(separator=' ', strip=True),
               'details':  cells[3].get_text(separator=' ', strip=True),
               'notes':    cells[4].get_text(separator=' ', strip=True) if len(cells) >= 5 else "",
           }

           medalists_age_by_sport_data.append(row_data)

    # ===================================================================
    # convert into dataframes
    summer_sports_medalist_by_sport_df    = pd.DataFrame(summer_olympic_sports_data)
    winter_sports_medalist_by_sport_df    = pd.DataFrame(winter_olympic_sports_data)
    discontinued_summer_sports_df         = pd.DataFrame(discontinued_summer_sports_data)
    summer_sports_medalist_by_olympiad_df = pd.DataFrame(summer_olympiad_data)
    winter_sports_medalist_by_olympiad_df = pd.DataFrame(winter_olympiad_data)
    medalists_age_by_sport_df             = pd.DataFrame(medalists_age_by_sport_data)

    # ===================================================================
    # convert into csv files
    seeds_dir = '/usr/local/airflow/dags/dbt-env/olympics_dbt/seeds'

    os.makedirs(seeds_dir, exist_ok=True)

    summer_sports_medalist_by_sport_df.to_csv(f'{seeds_dir}/raw_summer_sports_medalist_by_sport.csv', index=False)
    winter_sports_medalist_by_sport_df.to_csv(f'{seeds_dir}/raw_winter_sports_medalist_by_sport.csv', index=False)
    discontinued_summer_sports_df.to_csv(f'{seeds_dir}/raw_discontinued_summer_sports.csv', index=False)
    summer_sports_medalist_by_olympiad_df.to_csv(f'{seeds_dir}/raw_summer_sports_medalist_by_olympiad.csv', index=False)
    winter_sports_medalist_by_olympiad_df.to_csv(f'{seeds_dir}/raw_winter_sports_medalist_by_olympiad.csv', index=False)
    medalists_age_by_sport_df.to_csv(f'{seeds_dir}/raw_medalists_age_by_sport.csv', index=False)