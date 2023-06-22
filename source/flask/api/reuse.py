connection = mysql.connector.connect(**config)
cursor = connection.cursor()
result = {}
now = datetime.now()
format_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
format_before = ""
if(data['TIME'] == "real time"):  
    dbName = data["DEVICEID"]+now.strftime("%Y%m%d")
    before = now - timedelta(milliseconds=50)
    # format_before = '2022-07-03 13:44:52.503283'
    # format_now = '2022-07-03 13:44:52.643283'
    format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f')
    # sql = "SELECT * FROM RadarData WHERE 'TIMESTAMP' > ('%s') AND 'TIMESTAMP' < ('%s')" % (format_before, format_now)
    sql = "SELECT * FROM "+dbName+" WHERE TIMESTAMP BETWEEN '%s' AND '%s'" % (format_before, format_now)
    cursor.execute(sql)
    # result["SQL"] = sql
    # cursor.execute("SELECT * FROM RadarData")
    result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP, "X": X, "Y": Y, "Z": Z} for (ID, TIMESTAMP, X, Y, Z) in cursor]
    # connection.commit()
    # result = cursor
    # print(result)
    cursor.close()
    connection.close()
# print(data)
else:
    dbName = data["DEVICEMAC"]+now.strftime("%Y%m%d")
    
    if not data["CUSTOM"]:
        t = data['TIME'].split(" ")[0]
        if "MINUTE" in data['TIME']:                                        
            before = now - timedelta(minutes=int(t))                
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f')                    
        elif "HOUR" in data['TIME']:
            before = now - timedelta(hours=int(t))                
            format_before = before.strftime('%Y-%m-%d %H:%M:%S.%f')
        sql = "SELECT ID,TIMESTAMP, frameNum, pointCloud FROM "+dbName+" WHERE TIMESTAMP BETWEEN '%s' AND '%s'" % (format_before, format_now)
    else:
        ts = data['TIME'].split('-')
        if ts[0][:10] == ts[-1][1:11]:
            dbStr = ts[0][:10]
            dbStr = dbStr.replace('/', "")
            dbName = data["DEVICEMAC"]+dbStr
        # print(dbName)
        # print(ts[0][:10])
        # print(ts[-1][1:11])
        sql = "SELECT ID,TIMESTAMP, frameNum, pointCloud FROM "+dbName+" WHERE TIMESTAMP BETWEEN '%s' AND '%s'" % (ts[0], ts[-1])
    cursor.execute(sql)
    result["DATA"] = [{"ID": ID, "TIMESTAMP": TIMESTAMP, "frameNum": frameNum, "pointCloud": pointCloud.decode('utf-8')} for (ID, TIMESTAMP, frameNum, pointCloud) in cursor]
    cursor.close()
    connection.close()
    # return result