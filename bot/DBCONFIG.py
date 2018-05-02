import pymysql

dbconfig = {
    'host': '',
    'user': '',
    'passwd': '',
    'db': ''
}

con = pymysql.connect(host = dbconfig['host'], user = dbconfig['user'],
    passwd = dbconfig['passwd'], db = dbconfig['db'])
cur = con.cursor()
