from mysql.connector import MySQLConnection

# dataBase = mysql.connector.connect(
#     host = 'localhost',
#     user = 'root',
#     passwd = 'admin'
# )

dataBase = MySQLConnection(host='localhost', user='root', password='admin')


cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE CRM")

print("All done")