import mysql.connector
from user.config import config

from collections import defaultdict
from user.email.gmail import sentMail
from user.email.gmailTemplate import emailTemplate
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

config = config()

def resetPasswordLink(data):
    result = defaultdict(list)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    if not re.fullmatch(regex, data):        
        sql = "SELECT * FROM USERS WHERE ID='%s'"%(data)
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        if not dbresult:
            result['ERROR'].append({'ID': 'User not found'})
            return result
        body = emailTemplate(dbresult[1], "https://aswelfarehome.gaitmetrics.org/api/updatePassword?"+str(dbresult[1])+"&"+str(dbresult[8])+"&update", "update")
        sentMail(dbresult[3], 'Request to change password', body)        
    else:
        sql = "SELECT * FROM USERS WHERE EMAIL='%s'"%(data)
        cursor.execute(sql)
        dbresult = cursor.fetchone()
        if not dbresult:
            result['ERROR'].append({'EMAIL': 'Email not found'})
            return result
        body = emailTemplate(dbresult[1], "https://aswelfarehome.gaitmetrics.org/api/updatePassword?"+str(dbresult[1])+"&"+str(dbresult[8])+"&update", "update")
        sentMail(dbresult[3], 'Request to change password', body)
    cursor.close()
    connection.close()
    result['DATA'].append({"CODE": 0})    
    return result