import mysql.connector
import re
from requests import get

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")
print(my_db)
if my_db:
    print('m am conectat')
else:
    print('nu m am conectat')
link_inp = input('provide a link: ')
nota_imp = input('provide rhe score: ')
last_episode_imp = input('provide the last episode: ')
date_imp = input('data ultimei vizionari: ')

url = get(link_inp)
request = url.text

pos_incep_titlu = re.search('<h1 class="">', url.text).span()[1]
pos_sf_titlu = re.search('</h1>', url.text).span()[0] - 18  # eliminam caracterele de la titlu pana la </h1>
title_found = request[pos_incep_titlu:pos_sf_titlu]
print(title_found, nota_imp)

pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', url.text).span()[1]
pos_sf_nr_ep = re.search('episodes</span>', url.text).span()[0] - 1  # am eliminat spatiul de dupa nr
nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
print(nr_of_ep, 'episoade')


my_cursor = my_db.cursor()

sql_com = "INSERT INTO tvseriesandscore(title,link,score,nr_episodes,last_seen_episode,the_date,snoozed) "\
          "VALUES (%s,%s,%s,%s,%s,%s,%s)"

new_serial = [(title_found,link_inp,nota_imp,nr_of_ep,last_episode_imp,date_imp, 0)]

my_cursor.executemany(sql_com, new_serial)

my_db.commit()

