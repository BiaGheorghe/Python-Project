import mysql.connector

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2")

my_cursor = my_db.cursor()
create_db = 'create database tvseries'
my_cursor.execute(create_db)
show_db = 'Show databases'
my_cursor.execute(show_db)
for db in my_cursor:
    print(db)
