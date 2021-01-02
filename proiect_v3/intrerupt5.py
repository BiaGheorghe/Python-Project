import time
import threading

from pip._vendor.distlib.compat import raw_input
from requests import get
import mysql.connector
import re
from bs4 import BeautifulSoup
import sys

try:
    my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")
except mysql.connector.Error as err:
    print("Something went wrong: {}".format(err) + 'Nu s-a putut realiza conexiunea...reporniti aplicatia si incercat '
                                                   'din nou')
    sys.exit()


# pe de-o parte cu ajutorul unui thread o data la 5 secunde o sa verific daca datele luate cu ajutorul linkurilor
# difera fata de datele din baza de date
class TheUpdate(threading.Thread):
    def __init__(self):
        super().__init__()
        self.my_timer = time.time()  # initializez variabila time la ora curenta

    def restart(self):
        self.my_timer = time.time() + 120
        # variabila my_timer reprezinta ora exacta la care trebuie sa ajunga variabila
        # time pentru a face din nou restart

    def run(self, *args):
        self.restart()
        while 1:
            if time.time() >= self.my_timer:
                # aici fac verificarile de update
                #ia toate linkurile si verifica cate episoade sunt in toatl pentru fiecare link si le compara cu cele din baza de date
                self.restart()  # resetez timpul


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
    title = s[10:len(s) - 2]
    score = s[len(s) - 1:len(s)]
    selectul = "UPDATE tvseries_and_score SET score = %s WHERE title = %s "
    values = (score, title)
    nr_rows = my_cursor.execute(selectul, values)
    if nr_rows is not None:
        my_db.commit()
    else:
        print('nu exista niciun film cu acest titlu... incearca din nou')


def set_date(s):
    my_cursor = my_db.cursor()
    title = s[9:len(s) - 11]
    date = s[len(s) - 10:len(s)]
    selectul = "UPDATE tvseries_and_score SET the_date = %s WHERE title = %s "
    values = (date, title)
    nr_rows = my_cursor.execute(selectul, values)
    if nr_rows is not None:
        my_db.commit()
    else:
        print('nu exista niciun film')


def set_snooze(s):
    my_cursor = my_db.cursor()
    title = s[11:len(s) - 3]
    snooze = s[len(s) - 2:len(s)]
    selectul = "UPDATE tvseries_and_score SET snoozed = %s WHERE title = %s "
    values = (snooze, title)
    my_cursor.execute(selectul, values)
    my_db.commit()


def set_last_episode(s):
    my_cursor = my_db.cursor()
    s = s[::-1]  # oglinditul lui s
    ep_incep = re.search('e', s).span()[0]
    episode = s[0:ep_incep]
    print('episode- ', episode)
    sn_incep = re.search('s', s).span()[0]
    season = s[ep_incep + 1:sn_incep]
    print('sezon-', season)
    s = s[::-1]
    title = s[17:len(s) - (len(episode) + len(season) + 3)]
    print(title)
    sn_and_ep = 's' + season + 'e' + episode
    selectul = "UPDATE tvseries_and_score SET last_seen_episode = %s WHERE title = %s "
    values = (sn_and_ep, title)
    my_cursor.execute(selectul, values)
    my_db.commit()


def suggestions():
    my_cursor = my_db.cursor(buffered=True)
    selectul = "select title, score from tvseries_and_score order by score desc "
    my_cursor.execute(selectul)
    result_set = my_cursor.fetchall()
    for result in result_set:
        title1 = result[0]
        score1 = result[1]
        print('-', title1, '-', score1)
        my_cursor1 = my_db.cursor(buffered=True)
        selectul = "select last_seen_episode from tvseries_and_score WHERE title = %s and score= %s "
        info = (title1, score1)
        my_cursor1.execute(selectul, info)
        result_set_1 = my_cursor1.fetchall()
        if not result_set_1:
            for result1 in result_set_1:
                sn_and_ep = result1[0]
                end_sn = re.search('e', sn_and_ep).span()[0]
                season = int(sn_and_ep[1:end_sn])
                print('season: ', season)
                episode = int(sn_and_ep[end_sn + 1:len(sn_and_ep)])
                print('episode: ', episode)
            my_cursor1.close()
        else:
            print('acest serial nu are setat ultimul episod vizionat... incercati comanda set_last episode')

    my_cursor.close()


def instructions():
    print('INSTRUCTIONS:')


def get_data(s):  # de verificat daca linkul exists valid
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
        print(int(nr_of_ep), ' :episoade')

        pos_incep_season = re.search('season=', url.text).span()[1]
        pos_sf_seasons = re.search('&nbsp;&nbsp;', url.text).span()[0] - 8
        nr_seasons = int(request[pos_incep_season:pos_sf_seasons])
        print(nr_seasons, ' :nr_seasons')

        score = raw_input('precizati nota: ')
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

        last_seen_ep = input("precizati ultimul ep vizionat: ")  # de verificat daca e intre 0 si nr de ep aparute pt
        # fiecare sezon
        date = raw_input('data ultimei vizionari: ')  # de verificat daca e data valida (dupa ce a aparut serialul)
        # si pana in data curenta
        if date == '':
            date = '0000-00-00'
            print(date)
        else:
            print(date)
        snoozed = input('vreti sa primiti notificari de episoade noi? ')  # de verificat daca e da sau nu
        my_cursor = my_db.cursor()
        sql_com = "INSERT INTO tvseries_and_score(title,link,score,nr_episodes, nr_seasons, last_seen_episode, " \
                  "the_date, " \
                  "snoozed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
        tv_series = [(title, s, score, nr_of_ep, nr_seasons, last_seen_ep, date, snoozed)]
        my_cursor.executemany(sql_com, tv_series)
        my_db.commit()

        my_cursor = my_db.cursor()
        selectul = 'select id from tvseries_and_score where title=title'
        my_cursor.execute(selectul)
        result_set = my_cursor.fetchall()
        for result in result_set:
            resultant = result[0]  # resultant sigur exista deroarece reprezinta id-ul serialului tocmai adaugat in
            # baza de date

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
    else:
        print("nu e buna comanda")


t = TheUpdate()
t.start()
# pe de alta parte iau comenzile date de la tastatura si le prelucrez
while 1:
    x = input()
    # aici introduc comenzile de la tastatura
    execute_command(x)
    t.restart()
