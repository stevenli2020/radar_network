import unittest
from unittest.mock import patch, MagicMock
from collections import defaultdict
import mysql.connector

from user.passwordManager import *

# Assuming addPassword function is in the script user_script.py
# from user_script import addPassword

class TestAddPassword(unittest.TestCase):

  @patch('mysql.connector.connect')
  def test_add_password(self, mock_connect):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Test case where login name is empty
    data = {
        'LOGIN_NAME': '',
        'PWD': 'password123',
        'CPWD': 'password123',
        'CODE': 'ABC123'
    }
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'Username': 'Username is Empty!'}]})
    self.assertEqual(result, expected_result)

    # Test case where password is empty
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': '',
        'CPWD': 'password123',
        'CODE': 'ABC123'
    }
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'PWD': 'Password is Empty!'}]})
    self.assertEqual(result, expected_result)

    # Test case where confirm password is empty
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': 'password123',
        'CPWD': '',
        'CODE': 'ABC123'
    }
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'CPWD': 'Confirm Password is Empty!'}]})
    self.assertEqual(result, expected_result)

    # Test case where password and confirm password do not match
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': 'password123',
        'CPWD': 'password456',
        'CODE': 'ABC123'
    }
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'CPWD': 'Password must be same!'}]})
    self.assertEqual(result, expected_result)

    # Test case where code is empty
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': 'password123',
        'CPWD': 'password123',
        'CODE': ''
    }
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'Username': 'Unauthorized User!'}]})
    self.assertEqual(result, expected_result)

    # Test case where username is incorrect
    data = {
        'LOGIN_NAME': 'wronguser',
        'PWD': 'password123',
        'CPWD': 'password123',
        'CODE': 'ABC123'
    }
    mock_cursor.fetchone.return_value = ('testuser', 'ABC123', 'oldpassword')
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'Username': 'Username is incorrect!'}]})
    self.assertEqual(result, expected_result)

    # Test case where code is incorrect
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': 'password123',
        'CPWD': 'password123',
        'CODE': 'WRONG123'
    }
    mock_cursor.fetchone.return_value = ('testuser', 'ABC123', 'oldpassword')
    result = addPassword(data)
    expected_result = defaultdict(list, {'ERROR': [{'Username': 'Unauthorized User!'}]})
    self.assertEqual(result, expected_result)

    # Test case where everything is correct
    data = {
        'LOGIN_NAME': 'testuser',
        'PWD': 'password123',
        'CPWD': 'password123',
        'CODE': 'ABC123'
    }
    mock_cursor.fetchone.return_value = ('testuser', 'ABC123', 'oldpassword')
    result = addPassword(data)
    expected_result = defaultdict(list, {'CODE': 0})
    self.assertEqual(result, expected_result)
    mock_cursor.execute.assert_called_with("UPDATE USERS SET PWD='password123', STATUS='1' WHERE CODE='ABC123'")
    self.assertTrue(mock_connection.commit.called)
    self.assertTrue(mock_cursor.close.called)
    self.assertTrue(mock_connection.close.called)

if __name__ == '__main__':
  unittest.main()
