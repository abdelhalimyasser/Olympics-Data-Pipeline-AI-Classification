from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
from include.scrapper import scrapper


default_args = {
    'owner': 'abdelhalimyasser',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='olympics_pipeline',
    default_args=default_args,
    description='A DAG to scrape Olympic medalists data and store it in CSV files for dbt processing',
    start_date=datetime(2024, 6, 1),
    schedule='@daily',
    catchup=False,
    tags=['olympics', 'scraping', 'dbt']
) as dag:
    
    scraping_task = PythonOperator(
        task_id='scraping_task',
        python_callable=scrapper
    )

    dbt_run_task = BashOperator(
        task_id='dbt_run_task',
        bash_command='cd /usr/local/airflow/dags/dbt-env/olympics_dbt && dbt run --profiles-dir .'
    )

    export_data_task = BashOperator(
        task_id='export_data_task',
        bash_command='cd /usr/local/airflow/dags/dbt-env/olympics_dbt && python export_data.py'
    )

    scraping_task >> dbt_run_task >> export_data_task
    