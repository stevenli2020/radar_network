import unittest
from unittest.mock import patch, MagicMock
import mysql.connector

from user.usersManagement import requestAllUsers, requestSpecificUser, addNewUser, updateUserDetails, deleteUserDetails, getMQTTClientID, setClientConnection

class TestUsersManagement(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_requestAllUsers(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.__iter__.return_value = iter([
        (1, 'login_name', 'full_name', 'email@example.com', '1234567890', 'type', 'status', 'code', None, None, 'room_name')
    ])

    result = requestAllUsers()
    self.assertIn("DATA", result)
    self.assertEqual(len(result["DATA"]), 1)
    self.assertEqual(result["DATA"][0]["LOGIN_NAME"], "login_name")

  @patch('mysql.connector.connect')
  def test_requestSpecificUser(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.__iter__.return_value = iter([
        (1, 'login_name', 'full_name', 'email@example.com', '1234567890', 'type', 'status', 'code', None, None, 'room_name')
    ])

    result = requestSpecificUser({'USER_ID': 1})
    self.assertIn("DATA", result)
    self.assertEqual(len(result["DATA"]), 1)
    self.assertEqual(result["DATA"][0]["LOGIN_NAME"], "login_name")

  @patch('mysql.connector.connect')
  def test_addNewUser(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.side_effect = [None, None]  # User not found in both queries

    # Mock email template and sending function

    data = {
        'LOGIN_NAME': 'test_user',
        'FULL_NAME': 'Test User',
        'EMAIL': 'test_user@example.com',
        'PHONE': '1234567890',
        'USER_TYPE': '1',
        'ROOM': 'Room1, Room2'
    }
    result = addNewUser(data)
    self.assertIn("DATA", result)
    self.assertEqual(result["DATA"][0]["CODE"], 0)

  @patch('mysql.connector.connect')
  def test_updateUserDetails(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = [(1, 'old_login', 'full_name', 'old_email@example.com', '1234567890', 'type', 'status', 'code', None, None),None,None,None] # (1, 'old_login', 'full_name', 'old_email@example.com', '1234567890', 'type', 'status', 'code', None, None)

    data = {
        'USER_ID': 1,
        'LOGIN_NAME': 'new_login',
        'FULL_NAME': 'New Full Name',
        'EMAIL': 'new_email@example.com',
        'PHONE': '0987654321',
        'USER_TYPE': '1',
        'ROOM': 'Room1, Room2'
    }

    result = updateUserDetails(data)
    self.assertIn("ERROR", result)

  @patch('mysql.connector.connect')
  def test_deleteUserDetails(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.side_effect = [
        (1, 'login_name', 'full_name', 'email@example.com', '1234567890', 'type', 'status', 'code', None, None)  # Existing user
    ]

    data = {
        'USER_ID': 1
    }
    result = deleteUserDetails(data)
    self.assertIn("DATA", result)
    self.assertEqual(result["DATA"][0]["CODE"], 0)

  @patch('mysql.connector.connect')
  def test_getMQTTClientID(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.side_effect = [
        [{'client_id': 'client_id_1'}],  # Available client ID
        []  # No available client ID
    ]

    username = 'test_user'
    client_id = getMQTTClientID(username)
    self.assertEqual(client_id, 'client_id_1')

  @patch('mysql.connector.connect')
  def test_setClientConnection(self, mock_connect):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the SQL execution and result
    mock_cursor.execute.return_value = None

    client_id = 'client_id_1'
    status = setClientConnection(client_id)
    self.assertTrue(status)

if __name__ == "__main__":
  unittest.main()