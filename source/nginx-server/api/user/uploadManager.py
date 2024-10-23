import mysql.connector
from user.config import config
from datetime import datetime, timedelta
from user.parseFrame import *
import pytz
import copy
from collections import defaultdict

config = config()
now = datetime.now()
format_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')

def uploadImgFile(data):
    print(data)
    return data

