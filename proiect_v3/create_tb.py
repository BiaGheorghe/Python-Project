import mysql.connector

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")

my_cursor = my_db.cursor()
create_table_tvSeries = 'create table tvSeries_And_Score(id INT(255) UNSIGNED AUTO_INCREMENT PRIMARY KEY, '\
                        'title varchar(100), '\
                        'link varchar(254), score int(10), ' \
                        'nr_episodes int(255) , last_seen_episode int(255),the_date date, snoozed varchar(4)) '
my_cursor.execute(create_table_tvSeries)
show_tables = 'show tables'
my_cursor.execute(show_tables)
for tb in my_cursor:
    print(tb)
