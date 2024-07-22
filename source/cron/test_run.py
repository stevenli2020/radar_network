import unittest
from unittest.mock import patch, MagicMock

from run import *

test_config = {
  'user': 'flask',
  'password': 'CrbI1q)KUV1CsOj-',
  'host': '143.198.199.16',
  'port': '2203',
  'database': 'Gaitmetrics'
}

class TestCron(unittest.TestCase):

  def test_is_abnormal(self):
    result = is_abnormal(15,[1,1,2,3,4,5])
    self.assertTrue(result)

    result = is_abnormal(15,[14,14,12,13,14,5],threshold=5)
    self.assertFalse(result)

  def test_get_interval_tables(self):
    expected = [
      "PROCESSED_DATA_2024_07_01",
      "PROCESSED_DATA_2024_07_02",
      "PROCESSED_DATA_2024_07_03",
      "PROCESSED_DATA_2024_07_04",
      "PROCESSED_DATA_2024_07_05",
      "PROCESSED_DATA_2024_07_06",
      "PROCESSED_DATA_2024_07_07"
    ]

    connection = mysql.connector.connect(**test_config)
    cursor = connection.cursor(dictionary=True)
    result,curr = get_interval_tables(cursor,"2024-07-07")
    cursor.close()
    connection.close()
    self.assertEqual(result , expected)

  def test_get_table_dates_between(self):
    expected = [
      "PROCESSED_DATA_2024_07_01",
      "PROCESSED_DATA_2024_07_02",
      "PROCESSED_DATA_2024_07_03",
      "PROCESSED_DATA_2024_07_04",
      "PROCESSED_DATA_2024_07_05",
      "PROCESSED_DATA_2024_07_06",
      "PROCESSED_DATA_2024_07_07"
    ]

    connection = mysql.connector.connect(**test_config)
    cursor = connection.cursor(dictionary=True)
    result = get_table_dates_between(cursor, "2024-07-01", "2024-07-07")
    cursor.close()
    connection.close()
    self.assertEqual(result , expected)

  def test_check_table_exist(self):
    connection = mysql.connector.connect(**test_config)
    cursor = connection.cursor(dictionary=True)

    result = check_table_exist(cursor, "PROCESSED_DATA_2024_01_01")
    self.assertTrue(result)
    result = check_table_exist(cursor, "PROCESSED_DATA_2099_01_01")
    self.assertFalse(result)

    cursor.close()
    connection.close()

  def test_analyse_position_data(self):
    data = []
    social, moving, upright, laying = analyse_position_data(data)
    self.assertEqual(social,"0m")
    self.assertEqual(moving,"0m")
    self.assertEqual(upright,"0m")
    self.assertEqual(laying,"0m")

  def test_get_week_start_end(self):
    exp_start = datetime.date(2024, 7, 1)
    exp_end = datetime.date(2024, 7, 7)
    start, end = get_week_start_end("2024-07-01")
    self.assertEqual(start, exp_start)
    self.assertEqual(end, exp_end)

  def test_same_weekday(self):
    result = same_weekday("2024-07-01","2024-07-08")
    self.assertTrue(result)

    result = same_weekday("2024-07-01","2024-07-07")
    self.assertFalse(result)

  def test_text_to_seconds(self):
    result = text_to_seconds("1m")
    self.assertEqual(result,60)

    result = text_to_seconds("1m1s")
    self.assertEqual(result,61)

    result = text_to_seconds("1h1m")
    self.assertEqual(result,3660)

  @patch('mysql.connector.connect')
  def test_get_data_types(self, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.__iter__.return_value = iter([
        (1, 'data_key_1', 'Data Label 1'),
        (2, 'data_key_2', 'Data Label 2')
    ])

  def test_is_nap(self):
    data = [
      { "start":datetime.datetime(2024,7,1,17,0,0), "end":datetime.datetime(2024,7,2,7,0,0), "result":False },
      { "start":datetime.datetime(2024,7,1,12,0,0), "end":datetime.datetime(2024,7,1,14,0,0), "result":True },
      { "start":datetime.datetime(2024,7,1,9,0,0), "end":datetime.datetime(2024,7,1,11,0,0), "result":True },
    ]

    for d in data:
      result = is_nap(d.get("start"),d.get("end"))
      self.assertEqual(result,d.get("result"))