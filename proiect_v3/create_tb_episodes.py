import mysql.connector

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")

my_cursor = my_db.cursor()
create_table_episodes = 'create table episodes(id INT(255) UNSIGNED AUTO_INCREMENT PRIMARY KEY, season int(100), ' \
                        'episode int(100), title varchar(100)) '
my_cursor.execute(create_table_episodes)
show_tables = 'show tables'
my_cursor.execute(show_tables)
for tb in my_cursor:
    print(tb)
