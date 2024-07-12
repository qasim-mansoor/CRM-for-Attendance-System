import datetime
from django.db import connection

from mysql.connector import MySQLConnection

# dataBase = mysql.connector.connect(
#     host = 'localhost',
#     user = 'root',
#     passwd = 'admin'
# )

dataBase = MySQLConnection(host='localhost', user='root', password='admin', database='crm')

cursor = dataBase.cursor()

sql = """
DELIMITER //
CREATE TRIGGER updateDueDate 
AFTER INSERT, UPDATE 
ON website_customer
FOR EACH ROW
BEGIN
    IF NEW.last_paid IS NOT NULL THEN
        SET NEW.due_date = DATE_ADD(NEW.last_paid, INTERVAL 1 MONTH);
    END IF;
END;
//
DELIMITER ;
"""

try:
    cursor.execute(sql)
except Exception as e:
    print("Error creating trigger:", e)
else:
    print("Trigger created successfully.")

cursor.close()