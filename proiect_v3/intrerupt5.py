import time
import threading
from requests import get

import mysql.connector
import re

my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")


# de verificat daca se realizeaza conexiunea


# pe de-o parte cu ajutorul unui thread o data la 5 secunde o sa verific daca datele luate cu ajutorul linkurilor
# difera fata de datele din baza de date
class TheUpdate(threading.Thread):
    def __init__(self):
        super().__init__()
        self.my_timer = time.time()  # initializez variabila time la ora curenta

    def restart(self):
        self.my_timer = time.time() + 5
        # variabila my_timer reprezinta ora exacta la care trebuie sa ajunga variabila
        # time pentru a face din nou restart

    def run(self, *args):
        self.restart()
        while 1:
            if time.time() >= self.my_timer:
                # print("a expirat timpul")
                # aici fac verificarile de update
                self.restart()  # resetez timpul


def display_movies():  # de verificat daca sunt filme de afisat in tabela
    my_cursor = my_db.cursor()
    selectul = 'select * from tvseries_and_score'
    my_cursor.execute(selectul)
    result_set = my_cursor.fetchall()
    for row in result_set:
        print(row[1])


def get_data(s):  # de verificat daca linkul este valid
    url = get(s)
    request = url.text

    pos_incep_titlu = re.search('<h1 class="">', url.text).span()[1]
    pos_sf_titlu = re.search('</h1>', url.text).span()[0] - 18  # eliminam caracterele de la titlu pana la </h1>
    title = request[pos_incep_titlu:pos_sf_titlu]
    print(title, ' :titlul')
    # de verificat daca mai e o data in tabela

    pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', url.text).span()[1]
    pos_sf_nr_ep = re.search('episodes</span>', url.text).span()[0] - 1  # am eliminat spatiul de dupa nr
    nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
    print(nr_of_ep, ' :episoade')

    score = input("precizati nota: ")  # de verificat daca e intre 0 si 10
    # print(score, " :nota")
    if score == '':
        score = "NULL"
        print(score, "jhgku")
    last_seen_ep = input("precizati ultimul ep vizionat: ")  # de verificat daca e intre 0 si nr de ep aparute
    if last_seen_ep == "":
        last_seen_ep = 'NULL'
    date = input(
        'data ultimei vizionari: ')  # de verificat daca e data valida (dupa ce a aparut serialul) si pana in data curenta
    if date == "":
        date = 'NULL'
    snoozed = input('vreti sa primiti notificari de episoade noi? ')  # de verificat daca e da sau nu
    if snoozed == "":
        snoozed = 'NULL'

    my_cursor = my_db.cursor()
    sql_com = "INSERT INTO tvseries_and_score(title,link,score,nr_episodes, last_seen_episode, the_date, snoozed) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    tv_series = [(title, s, score, nr_of_ep, last_seen_ep, date, snoozed)]
    my_cursor.executemany(sql_com, tv_series)
    my_db.commit()


def execute_command(command):
    if command == 'display':
        display_movies()
    elif command[0:20] == 'https://www.imdb.com':
        get_data(command)
    else:
        print("nu e buna comanda")


t = TheUpdate()
t.start()
# pe de alta parte iau comenzile date de la tastatura si le prelucrez
while 1:
    x = input()
    # aici introduc comenzile de la tastatura
    print('\nYou entered %r\n' % x)
    execute_command(x)
    t.restart()
