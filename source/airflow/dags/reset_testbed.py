from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
import mysql.connector

from constants import vernemq

env = "testbed"


def reset_connection():

    vernemq_connection = mysql.connector.connect(**vernemq(env))
    vernemq_cursor = vernemq_connection.cursor(dictionary=True)
    sql = "UPDATE vmq_auth_acl SET connected=0,last_connect_time=NOW() WHERE connected=1 AND TIMESTAMPDIFF(MINUTE, last_connect_time, NOW()) > 5;"
    vernemq_cursor.execute(sql)
    vernemq_connection.commit()
    vernemq_cursor.close()
    vernemq_connection.close()
    print("Finished removed!")


def notify_email(context):
    subject = f"Airflow alert: {context['task_instance'].task_id} Failed"
    body = f"""
  DAG: {context['task_instance'].dag_id}<br>
  Task: {context['task_instance'].task_id}<br>
  Execution Time: {context['execution_date']}<br>
  Log: <a href="{context['task_instance'].log_url}">Log</a>
  """
    send_email("mvplcw97@gmail.com", subject, body)


with DAG(
    dag_id="reset_dag_testbed",
    start_date=datetime(2024, 10, 12),
    schedule_interval="*/5 * * * *",
    catchup=False,
) as dag:

    reset_connection_task = PythonOperator(
        task_id="RESET_CONNECTION",
        python_callable=reset_connection,
        on_failure_callback=notify_email,
    )

