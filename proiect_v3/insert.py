import mysql.connector

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")

my_cursor = my_db.cursor()

sql_com = "INSERT INTO tvseries(title,score) VALUES (%s,%s)"

tv_series=[('titlu1',9),('titlu2'),6]

my_cursor.executemany(sql_com, tv_series)

my_db.commit()
