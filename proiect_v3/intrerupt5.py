# import time
# import threading
import requests
from requests import get
import mysql.connector
import re
import sys
import datetime
from bs4 import BeautifulSoup

try:
    my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")
except mysql.connector.Error as err:
    print("Something went wrong: {}".format(err) + 'Nu s-a putut realiza conexiunea...reporniti aplicatia si incercat '
                                                   'din nou')
    sys.exit()


# pe de-o parte cu ajutorul unui thread o data la 5 secunde o sa verific daca datele luate cu ajutorul linkurilor
# difera fata de datele din baza de date

# class TheUpdate(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         self.my_timer = time.time()  # initializez variabila time la ora curenta
#
#     def restart(self):
#         self.my_timer = time.time() + 120
#         news()
#         # variabila my_timer reprezinta ora exacta la care trebuie sa ajunga variabila
#         # time pentru a face din nou restart
#
#     def run(self, *args):
#         self.restart()
#         while 1:
#             if time.time() >= self.my_timer:
#                 # aici fac verificarile de update ia toate linkurile si verifica cate episoade sunt in toatl pentru
#                 # fiecare link si le compara cu cele din baza de date
#                 self.restart()  # resetez timpul


def create_db():
    try:
        my_db1 = mysql.connector.connect(host="localhost", user="bia", passwd="bia2")
    except mysql.connector.Error as error:
        print(str(error)[0:5] + "Something went wrong: {}".format(
            err) + 'Nu s-a putut realiza conexiunea...reporniti aplicatia si incercati din nou')
        sys.exit()

    ok_db = 1
    my_cursor = my_db1.cursor()
    task: str = 'create database tvseries'
    try:
        my_cursor.execute(task)
        print('data de baze a fost creata cu succes')
    except mysql.connector.Error as error:
        print(str(error)[0:5] + ' -data de baze exista')
        ok_db = 0
    if ok_db == 1:
        show_db = 'Show databases'
        my_cursor.execute(show_db)
        for db in my_cursor:
            print(db)


def create_tb():
    ok_tv: int = 1
    my_cursor = my_db.cursor()
    create_table_tvSeries = 'create table tvSeries_And_Score(id INT(255) UNSIGNED AUTO_INCREMENT PRIMARY KEY, ' \
                            'title varchar(100), ' \
                            'link varchar(254), score int(10), ' \
                            'nr_episodes int(255) ,nr_seasons int(255), last_seen_episode varchar (7),the_date date, ' \
                            'snoozed varchar(4)) '
    try:
        my_cursor.execute(create_table_tvSeries)
        print('-Tabela tv_series_and_score a fost creata cu succes')
    except mysql.connector.Error as the_err:
        print(str(the_err)[0:5] + '-Tabela tv_series_and_score exista')
        ok_tv = 0
    if ok_tv == 1:  # afisarea tabelelor
        show_tables = 'show tables'
        my_cursor.execute(show_tables)
        for tb in my_cursor:
            print(tb)


def create_tb_episodes():
    ok_ep: int = 1
    my_cursor = my_db.cursor()
    create_table_episodes = 'create table episodes(id INT(255) UNSIGNED AUTO_INCREMENT PRIMARY KEY, serial int(255), ' \
                            'season int(100), episode int(100), title varchar(100)) '
    try:
        my_cursor.execute(create_table_episodes)
        print('-Tabela episodes a fost creata cu succes')
    except mysql.connector.Error as an_err:
        print(str(an_err)[0:5] + ' -Tabela episodes exista')
        ok_ep = 0
    if ok_ep == 1:
        show_tables = 'show tables'
        my_cursor.execute(show_tables)
        for tb in my_cursor:
            print(tb)


def display_titles():
    my_cursor = my_db.cursor(buffered=True)
    selectul = 'select * from tvseries_and_score'
    my_cursor.execute(selectul)
    result_set = my_cursor.fetchall()
    if not result_set:
        print('nu esxista titluri adaugate')
    else:
        for row in result_set:
            print(row[1])
            my_cursor.close()


def set_score(s):
    my_cursor = my_db.cursor()
    s = s[::-1]
    score_fin = re.search(" ", s).span()[0]
    score = s[0:score_fin]
    print('score: ' + score)
    s = s[::-1]
    title = s[10:len(s) - len(score) - 1]
    print('title: ', title)
    if 10 >= int(score) >= 0:
        selectul = "UPDATE tvseries_and_score SET score = %s WHERE title = %s "
        values = (score, title)
        my_cursor.execute(selectul, values)
        my_db.commit()
        rowsaffected = my_cursor.rowcount
        if rowsaffected == 0:
            print("nu exista serial cu acest titllu in lista")
        else:
            print('succes')
    else:
        print('nota pe care ati acordat-o nu este valida')


def set_date(s):
    my_cursor = my_db.cursor()
    title = s[9:len(s) - 11]
    date = s[len(s) - 10:len(s)]
    year, month, day = date.split('-')
    isValidDate = True
    try:
        date = datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        isValidDate = False
    now = datetime.datetime.now()
    if isValidDate:
        if int(now.year) >= int(year) and int(now.month) >= int(month) and int(now.day) >= int(day):
            print("Input date is valid ..")
            selectul = "UPDATE tvseries_and_score SET the_date = %s WHERE title = %s "
            values = (date, title)
            my_cursor.execute(selectul, values)
            my_db.commit()
            rowsaffected = my_cursor.rowcount
            if rowsaffected == 0:
                print("nu exista serial cu acest titllu in lista sau ati setat deja aceasta data")
            else:
                print('succes')
        else:
            print("Input date is not valid..")
    else:
        print("Input date is not valid..")


def set_snooze(s):
    my_cursor = my_db.cursor()
    title = s[11:len(s) - 3]
    snooze = s[len(s) - 2:len(s)]
    if snooze == 'da' or snooze == 'nu':
        selectul = "UPDATE tvseries_and_score SET snoozed = %s WHERE title = %s "
        values = (snooze, title)
        my_cursor.execute(selectul, values)
        my_db.commit()
        rowsaffected = my_cursor.rowcount
        if rowsaffected == 0:
            print("nu exista serial cu acest titllu in lista sau ati setat deja aceasta optiune")
        else:
            print('succes')
    else:
        print('invalid input...alegeti da sau nu')


def set_last_episode(s):
    ok_seasons = 1
    ok_episodes = 1
    s = s[::-1]  # oglinditul lui s
    ep_incep = re.search('e', s).span()[0]
    episode = s[0:ep_incep]
    episode = episode[::-1]
    print('episode- ', episode)
    sn_incep = re.search('s', s).span()[0]
    season = s[ep_incep + 1:sn_incep]
    print('sezon-', season)
    s = s[::-1]
    title1 = s[17:len(s) - (len(episode) + len(season) + 3)]
    print(title1)
    try:
        season = int(season[::-1])
    except ValueError as error:
        print(str(error)[0:5] + 'Comanda incorecta...Incercati din nou')
        ok_seasons = 0
    if ok_seasons == 1:
        my_cursor = my_db.cursor(buffered=True)
        selectul = 'select nr_seasons, id from tvseries_and_score where title = %s'
        info = (title1,)
        my_cursor.execute(selectul, info)
        result_set = my_cursor.fetchall()
        if len(result_set) != 0:
            for result in result_set:
                if result[0] != '':
                    print('result1: ------', result[0], '--------', result[1])
                    if 1 <= season <= int(
                            result[0]):  # daca nr de sezoane dat este mai mic sau egal cu nr de sez ale serial
                        my_cursor1 = my_db.cursor(buffered=True)
                        selectul1 = 'select id from episodes WHERE serial = %s and season= %s'  # nr cate ep are sezonul
                        info1 = (result[1], season)  # id-ul filmului si sezonul
                        my_cursor1.execute(selectul1, info1)
                        result_set1 = my_cursor1.fetchall()

                        try:
                            episode = int(episode[::-1])
                        except ValueError as error:
                            print(str(error)[0:5] + 'Comanda incorecta...Incercati din nou')
                            ok_episodes = 0
                        if ok_episodes == 1:

                            if 1 <= episode <= len(result_set1):
                                sn_and_ep = 's' + str(season) + 'e' + str(episode)
                                my_cursor2 = my_db.cursor(buffered=True)
                                selectul2 = "UPDATE tvseries_and_score SET last_seen_episode = %s WHERE title = %s "
                                values = (sn_and_ep, title1)
                                my_cursor2.execute(selectul2, values)
                                my_db.commit()
                                rowsaffected = my_cursor2.rowcount
                                if rowsaffected == 0:
                                    print("nu exista serial cu acest titllu in lista sau ati setat deja acest episod")
                                else:
                                    print('succes')
                            else:
                                print('nu exista episodul cu nr ' + str(episode) + ' in sezonul ' + str(season))
                    else:
                        print('nu exista sezonul cu numarul ' + str(season))
                else:
                    print('nu exista acest serial in lista')
            my_cursor.close()
        else:
            print(title1 + ' nu exista in lista')


def suggestions():
    my_cursor = my_db.cursor(buffered=True)
    selectul = "select title, score from tvseries_and_score order by score desc "
    my_cursor.execute(selectul)
    result_set = my_cursor.fetchall()
    if len(result_set) != 0:
        for result in result_set:
            title1 = result[0]
            score1 = result[1]
            print('-', title1, '-', score1)
            my_cursor1 = my_db.cursor(buffered=True)
            selectul = "select last_seen_episode from tvseries_and_score WHERE title = %s and score= %s "
            info = (title1, score1)
            my_cursor1.execute(selectul, info)
            result_set_1 = my_cursor1.fetchall()
            for result1 in result_set_1:
                if result1[0] != '':
                    print('result1: ------', result1[0])
                    sn_and_ep = result1[0]
                    end_sn = re.search('e', sn_and_ep).span()[0]
                    season = int(sn_and_ep[1:end_sn])
                    print('season: ', season)
                    episode = int(sn_and_ep[end_sn + 1:len(sn_and_ep)])
                    print('episode: ', episode)
                else:
                    print('acest serial nu are setat ultimul episod vizionat... incercati comanda set_last episode')
            my_cursor1.close()
        my_cursor.close()
    else:
        print('nu se pot face sugestii...nu exista niciun serial in lista')


def instructions():
    print('INSTRUCTIONS:')


def get_data(s):
    ok_ep = 1
    request = requests.get(s)
    if request.status_code == 200:
        print('Web site exists')
        resultant: int = 0  # l-am initializat cu 0 pentru a nu mai avea warning la id
        url = get(s)
        request = url.text

        pos_incep_titlu = re.search('<h1 class="">', url.text).span()[1]
        pos_sf_titlu = re.search('</h1>', url.text).span()[0] - 18  # eliminam caracterele de la titlu pana la </h1>
        title = request[pos_incep_titlu:pos_sf_titlu]
        print(title)

        my_cursor1 = my_db.cursor()
        selectul = 'select title from tvseries_and_score'
        my_cursor1.execute(selectul)
        result_set = my_cursor1.fetchall()
        exists: int = 0
        for result in result_set:
            if result[0] == title:  # verificam daca a mai fost adaugat o data
                exists = 1

        if exists == 0:
            id_film = s[27:36]
            print(id_film, ':id  film')

            pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', url.text).span()[1]
            pos_sf_nr_ep = re.search('episodes</span>', url.text).span()[0] - 1  # am eliminat spatiul de dupa nr
            nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
            try:
                print(int(nr_of_ep), ' :episoade')
            except ValueError as error:
                print(str(error)[0:5] + 'eroare la obtinerea numarului de episoade... verificati pagina ')
                ok_ep = 0
            if ok_ep == 1:
                pos_incep_season = re.search('season=', url.text).span()[1]
                pos_sf_seasons = re.search('&nbsp;&nbsp;', url.text).span()[0] - 8
                nr_seasons = int(request[pos_incep_season:pos_sf_seasons])
                print(nr_seasons, ' :nr_seasons')

                score = input('precizati nota: ')
                if score == '':
                    score = 0
                    print(score)
                else:
                    score_aux = int(score)
                    if (score_aux <= 10) and (0 <= score_aux):
                        score = score_aux
                        print(score)
                    else:
                        score = 0

                last_seen_ep = input(
                    "precizati ultimul ep vizionat: ")  # de verificat daca e intre 0 si nr de ep aparute pt
                # fiecare sezon
                date = input('data ultimei vizionari: ')
                # si pana in data curenta
                if date == '':
                    date = '0000-00-00'
                    print(date)
                else:
                    print(date)
                snoozed = input('doriti sa opriti notificarile de episoade noi pentru acest seruial? ')
                my_cursor = my_db.cursor()
                sql_com = "INSERT INTO tvseries_and_score(title,link,score,nr_episodes, nr_seasons, " \
                          "last_seen_episode, the_date, snoozed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
                tv_series = [(title, s, score, nr_of_ep, nr_seasons, last_seen_ep, date, snoozed)]
                my_cursor.executemany(sql_com, tv_series)
                my_db.commit()

                my_cursor = my_db.cursor()
                selectul = 'select id from tvseries_and_score where title=title'
                my_cursor.execute(selectul)
                result_set = my_cursor.fetchall()
                for result in result_set:
                    resultant = result[0]  # resultant sigur exista deroarece reprezinta id-ul serialului tocmai
                    # adaugat in baza de date

                for i in range(0, nr_seasons):
                    link = 'https://www.imdb.com/title/' + id_film + '/episodes?season=' + str(
                        i + 1) + '&ref_=tt_eps_sn_' + str(i + 1)
                    print(link, ':link')
                    url1 = get(link)
                    request1 = url1.text
                    soup = BeautifulSoup(request1, 'html.parser')
                    eptags = soup.select('strong')  # titlurile episoadelor
                    titles = [tag.text for tag in eptags]
                    j: int = 0
                    sql_com = "INSERT INTO episodes(serial, season, episode, title) VALUES (%s,%s,%s,%s) "
                    my_cursor = my_db.cursor()
                    while titles[j] != 'Season ' + str(i + 1):
                        print('serial: ', resultant, 'season: ', i + 1, 'ep: ', j + 1, 'nume: ', titles[j])
                        info = [(resultant, i + 1, j + 1, titles[j])]
                        my_cursor.executemany(sql_com, info)
                        my_db.commit()
                        j = j + 1

        else:
            print("acest serial a mai fost adaugat o data")
    else:
        print('Web site does not exist')


def news():
    my_cursor = my_db.cursor()
    task = 'select nr_episodes, link, id, title from tvseries_and_score'
    my_cursor.execute(task)
    result_set = my_cursor.fetchall()
    if len(result_set) != 0:
        for result in result_set:
            request = requests.get(result[1])
            if request.status_code == 200:  # iau fiecare link si verific daca e valid
                url = get(result[1])
                request = url.text
                pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', request).span()[1]
                pos_sf_nr_ep = re.search('episodes</span>', request).span()[0] - 1  # am eliminat spatiul de dupa nr
                nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
                if int(nr_of_ep) == int(result[0]):  # verificam daca e acelasi nr de episoade ca cele din baza de date
                    print('nimic nou')
                else:
                    print(result[3], '- are episoade noi aparute')
                    my_cursor = my_db.cursor()
                    task = 'delete from tvseries_and_score where link= %s'
                    info = (result[1],)
                    my_cursor.execute(task, info)
                    my_db.commit()
                    task = 'delete from episodes where serial = %s'
                    info = (result[2],)
                    my_cursor.execute(task, info)
                    my_db.commit()
                    get_data(result[1])

            else:
                print('link-ul nu mai e valid')
    else:
        print('lista e goala')


def execute_command(command):
    if command == 'display':
        display_titles()
    elif command[0:20] == 'https://www.imdb.com':
        get_data(command)
    elif command[0:9] == 'set_score':
        set_score(command)
    elif command[0:16] == 'set_last_episode':
        set_last_episode(command)
    elif command[0:8] == 'set_date':
        set_date(command)
    elif command[0:10] == 'set_snooze':
        set_snooze(command)
    elif command[0:11] == 'suggestions':
        suggestions()
    elif command[0:12] == 'instructions':
        instructions()
    elif command[0:4] == 'news':
        news()
    else:
        print("nu e buna comanda")


create_db()
create_tb()
create_tb_episodes()

# t = TheUpdate()
# t.start()
# pe de alta parte iau comenzile date de la tastatura si le prelucrez
while 1:
    x = input()
    # aici introduc comenzile de la tastatura
    execute_command(x)
    # t.restart() #restart dupa ce executa o comanda
