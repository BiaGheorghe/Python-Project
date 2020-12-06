import mysql.connector

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")

my_cursor = my_db.cursor()
create_table_tvSeries = 'create table tvSeries1( title varchar(50), score int(10)) '
my_cursor.execute(create_table_tvSeries)
show_tables = 'show tables'
my_cursor.execute(show_tables)
for tb in my_cursor:
    print(tb)
