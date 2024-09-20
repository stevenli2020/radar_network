#import schedule
import time
from datetime import datetime, timedelta
import subprocess
import mysql.connector
import os

config = {
    'user': 'flask',
    'password': 'CrbI1q)KUV1CsOj-',
    'host': 'db',
    'port': '3306',
    'database': 'Gaitmetrics'
    # 'user': 'root',
    # 'password': '14102022',
    # 'host': 'localhost',
    # 'port': '2203',
    # 'database': 'Gaitmetrics'
}

def archive_old_table():
  # Calculate the date 3 months ago
  three_months_ago = datetime.now() - timedelta(days=90)
  date_suffix = three_months_ago.strftime('%Y_%m_%d')
  table_name = f"PROCESSED_DATA_{date_suffix}"
  dump_file = f"/backup/{table_name}.sql"
  
  backup_dir = "/backup"
    
# Create the backup directory if it doesn't exist
  if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

  try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    # Dump the temporary table to a file
    dump_command = f"mysqldump -u{config['user']} -p{config['password']} -h{config['host']} {config['database']} {table_name} > {dump_file}"
    subprocess.run(dump_command, shell=True, check=True)

    # Drop the temporary table after dumping
    cursor.execute(f"DROP TABLE {table_name}")
    connection.commit()

    print(f"Table data dumped successfully: {dump_file}")

    # Optionally, delete old data from the original table
    #delete_old_data_sql = f"DELETE FROM your_table_name WHERE date_column <= '{three_months_ago.strftime('%Y-%m-%d')}'"
    #cursor.execute(delete_old_data_sql)
    #connection.commit()
    
    print(f"Old data deleted successfully from your_table_name")

  except mysql.connector.Error as err:
    print(f"Error: {err}")
  finally:
    cursor.close()
    connection.close()

archive_old_table()
