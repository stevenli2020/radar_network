from airflow import DAG
from airflow.operators.python import PythonOperator
import mysql.connector
from pytz import timezone
import datetime
from datetime import datetime as dt, timedelta
import re

from constants import config

env = "aswelfarehome"


def clean_data():
    prefix = "PROCESSED_DATA_"
    pattern = re.compile(r"^PROCESSED_DATA_(\d{4}_\d{2}_\d{2})$")
    keep_months = 6  # keep last 6 months
    cutoff_date = dt.today() - timedelta(days=keep_months * 30)  # ~6 months
    connection = mysql.connector.connect(**config(env))
    cursor = connection.cursor(dictionary=True)
    get_processed_data_query = f"SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'PROCESSED_DATA_%' ORDER BY table_name;"
    cursor.execute(get_processed_data_query)
    tables = cursor.fetchall()
    for table in tables:
        table_name = table["table_name"]
        match = pattern.match(table_name)
        if not match:
            print(f"Skipping {table_name}, does not match date format")
            continue
        try:
            date_str = match.group(1)  # "2024_01_01"
            table_date = dt.strptime(date_str, "%Y_%m_%d")

            if table_date < cutoff_date:
                drop_sql = f"DROP TABLE `{table_name}`"
                print(f"Dropping: {table_name}")
                cursor.execute(drop_sql)
                connection.commit()
        except Exception as e:
            print(f"Skipping {table_name}, error: {e}")

    print("Cleaning ROOM_TRACKER.")

    query = "DELETE FROM ROOM_TRACKER WHERE `TIMESTAMP` < NOW() - INTERVAL 10 DAY;"
    cursor.execute(query)
    connection.commit()

    connection.close()


with DAG(
    dag_id="weekly_clean_data_aswelfarehome",
    start_date=dt(2024, 10, 12),
    schedule_interval="59 23 * * 0",
    catchup=False,
) as dag:

    clean_data_task = PythonOperator(
        task_id="CLEAN_DATA",
        python_callable=clean_data,
    )

