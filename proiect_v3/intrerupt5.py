# import time
# import threading
import requests
from requests import get
import mysql.connector
import re
import sys
import datetime
from bs4 import BeautifulSoup
from youtubesearchpython import SearchVideos
import json

try:
    my_db = mysql.connector.connect(host="localhost", user="bia", passwd="bia2", database="tvseries")
except mysql.connector.Error as err:
    print("Something went wrong: {}".format(err) + 'Nu s-a putut realiza conexiunea...reporniti aplicatia si incercat '
                                                   'din nou')
    sys.exit()


# pe de-o parte cu ajutorul unui thread o data la 5 secunde o sa verific daca datele luate cu ajutorul linkurilor
# difera fata de datele din baza de date

# class TheUpdate(threading.Thread):
#     """Clasa care contine functiile de baza pentru firul de executie"""
#     def __init__(self):
#         """ Initializeaza variabila my_timer cu valoarea timpului curent. Nu returneaza nimic."""
#         super().__init__()
#         self.my_timer = time.time()
#
#     def restart(self):
#         """ Initializeaza variabila my_timer cu valoarea timpului curent la care se adauga 120 de secunde."""
#         self.my_timer = time.time() + 120
#
#     def run(self, *args):
#         """ Apeleaza functia restart() in momentul in care valoarea variabilei my_timer este mai mica sau egala decat
#         valoarea timpului curent. Nu returneaza nimic"""
#         self.restart()
#         while 1:
#             if time.time() >= self.my_timer:

#                 self.restart()  # resetez timpul


def create_db():
    """
    Se conecteaza la localhostt si daca nu exista exceptii creaza baza de date "tvseries" si afiseaza toate bazele de
    date existente ale userului.
    :param:
    :return:
    """
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
    """
    Daca nu exista exceptii creaza tabela "tvSeries_And_Score" si afiseaza toate tabelele din baza de date.
    din baza de date.
    :param:
    :return:
    """
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
    """
    Daca nu exista exceptii creaza tabela "episodes" si afiseaza toate tabelele din baza de date.
    :param:
    :return:
    """
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
    """
    Afiseaza toate titlurile serialelor ce sunt inregistrate in baza de date. Daca nu exista niciun titlu va afisa
    mesajul "nu exista titluri adaugate".
    :param
    :return:
    """
    my_cursor = my_db.cursor(buffered=True)
    selectul = 'select * from tvseries_and_score'
    my_cursor.execute(selectul)
    result_set = my_cursor.fetchall()
    if not result_set:
        print('nu exista titluri adaugate')
    else:
        for row in result_set:
            print(row[1])
            my_cursor.close()


def set_score(s):
    """
    Extrage din parametrul primit scorul si titlul, verifica daca scorul e valid. Daca e, face update in baza de date
    pentru tupla care contine titlul extras cu scorul verificat anterior si afiseaza mesajul "succes". Daca nu s-a
    facut update, afiseaza mesajul "nu exista serial cu acest titllu in lista". Daca insa scorul nu este valid, afiseaza
    mesajul "nota pe care ati acordat-o nu este valida"
    :param s:
    :return:
    """
    my_cursor = my_db.cursor()
    s = s[::-1]
    scor_valid = True
    score = None
    try:
        score_fin = re.search(" ", s).span()[0]
        score = int(s[0:score_fin])
    except ValueError:
        print('nu ati introdus scorul')
        scor_valid = False
    if scor_valid:
        print('score: ' + str(score))
        s = s[::-1]
        title = s[10:len(s) - len(str(score)) - 1]
        print('title: ', title)
        if 10 >= score >= 0:
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
    """
    Extrage din parametrul primit data si titlul si verifica daca data e valida prin ransformarea variabilei date din
    obiect de tip string in obiect de tip datetime. Daca data e valida, verifica sa nu depaseasca data curenta. Daca
    si acesta conditie e indeplinita, face update in baza de date pentru tupla care contine titlul extras cu data
    verificata anterior si afiseaza mesajul "succes". Daca update-ul nu s-a realizat, afiseaza mesajul "nu exista serial
    cu acest titllu in lista sau ati setat deja aceasta data". In cele 2 cazuri ramase in care validarea datei nu s-a
    realizat cu succes, va afisa mesajul "Data introdusa este invalida".
    :param s:
    :return:
    """
    my_cursor = my_db.cursor()
    title = s[9:len(s) - 11]
    date = s[len(s) - 10:len(s)]
    data_introdusa = True
    year, month, day = None, None, None
    try:
        year, month, day = date.split('-')
    except ValueError:
        print('nu ati introdus data corect')
        data_introdusa = False
    if data_introdusa:
        isValidDate = True
        try:
            date = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            isValidDate = False
        now = datetime.datetime.now()
        if isValidDate:
            if int(now.year) >= int(year):
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
                print("Data introdusa este invalida")
        else:
            print("Data introdusa este invalida")


def set_snooze(s):
    """
    Extrage din parametrul primit titlul si variabila snooze. Verifica daca valoarea variabilei snooze este valida.
    Daca da, face update in baza de date pentru tupla care contine titlul extras cu snooze si afiseaza mesajul "succes".
    Daca nu a fost realizat update-ul, afiseaza mesajul "nu exista serial cu acest titllu in lista sau ati setat deja
    aceasta optiune". Daca in schimb variabila snooze este invalida, afiseaza mesajul "input invalid..alegeti da sau nu"
    :param s:
    :return:
    """
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
        print('input invalid...alegeti da sau nu')


def set_last_episode(s):
    """
    Extrage numarul episodului, numarul sezonului si titlul din parametrul primit, le afiseaza si verifica daca au fost
    respectate  intructiunile cu privire la forma comenzii. Daca nu au fost respectate, va afisa mesaje corespunzatoare
    problemei. Daca au fost respectate, verifica daca titlul exista in lista. Daca exista, verifica daca numarul
    sezonului si numarul episodului sunt valide. Daca sunt, face update in baza de date pentru tupla care contine titlul
    extras cu valoarea variabilei sn_and_ep la last_seen_episode. Daca exista conditii care nu au fost indeplinite,
    va afisa mesaje corespunzatoare problemei intampinate.
    :param s:
    :return:
    """
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
        print(str(error)[0:5] + '\nComanda incorecta...Incercati din nou')
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
    """
    Afiseaza in ordine descrescatoare dupa scor toate titurile impreuna cu scorul si ultimul episod vizionat. Daca un
    serial nu are setat ultimul episod vizionat atunci afiseaza mesajul "acest serial nu are setat ultimul episod
    vizionat... incercati comanda set_last episode". Daca nu exista niciun serial in lista, afiseaza mesajul "nu se pot
    face sugestii...nu exista niciun serial in lista"
    :param:
    :return:
    """
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
    """
    Afiseaza toate modurile in care pot fi preluate corect comenzile date de catre utilizator de la tastatura
    :param:
    :return:
    """
    print('INSTRUCTIUNI:')
    print('1. display -Afisea toate titlurile pe care le-ati salvat pana acum.')
    print('2. *link_pentru_un_serial_de_pe_imbd* -Linkul trebuie sa inceapa cu "https://www.imdb.com"')
    print('3. set_score *titlu_serial* -Seteaza scorul pentru serialul dorit. Scorul trebuie sa fie un numar intrg '
          'intre 0 si 10. ')
    print('4. set_last_episode *titlu_serial* s*x*e*y* -Seteaza ultimul episod vizionat pentru serialul dorit. '
          'x-reprezinta numaru sezonului, y-reprezinta numarul episodului')
    print('5. set_date *titlu_serial* *yyyy-mm-dd* -Seteaza data ultimei vizionari pentru serialul dorit.')
    print('6. set_snooze *titlu_serial* *da/nu* -Hotaraste daca ati anulat sau nu notificarile pentru episoade noi '
          'pentru un anumit serial')
    print('7. suggestions -Afiseaza in ordine descrescatoare, in functie de nota, toate serialele si ultimul episod '
          'vizionat pentru fiecare dintre ele')
    print('8. news -verifica pentru toate serialele care au snoozed setat pe nu daca au aparut episoade noi')
    print('9. yt *target* -Cauta pe YouTube ce este in target si returneaza link-ul pentru primul videoclip gasit.')


def get_data(s):
    """
    Verifica daca link-ul primit ca parametru este valid si extrage din request titlul si il afiseaza. Daca titlul a
    mai fost adaugat o data in baza de date, afiseaza mesajul acest serial a mai fost adaugat o data". In caz contrar,
    extrage id-ul de pe site al serialului si numarul de episoade si le afiseaza. Daca site-ul nu e in forma corecta cu
    numarul de episoade in partea stanga a paginii, afiseaza mesajul "eroare la obtinerea numarului de episoade...
    verificati pagina". Daca numarul de episoade a fost extras corect, il afiseaza, extrage numerul de sezoane si
    asteapta input pentr scor, ultimul episod vazut, data si snoozed. Insereaza titlul, numarul de episoade, numarul de
    sezoane si datele mentionate anterior in tabela si pentru fiecare sezon introduce episoadele in tabela episodes.
    :param s:
    :return:
    """
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
                snoozed = input('doriti sa opriti notificarile de episoade noi pentru acest serial? ')
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
    """
    Verifica daca exista seriale care au optiunea snoozed pe 'nu' si cauta pentru ele daca numarul de episoade de pe
    site corespunde cu numarul de episoade din baza de date. In caz afirmativ, sterge tupla corespunzatoare serialului
    din tabela tvseries_and_score si toate episoadele din tabela episodes si apeleaza functia get_data cu  parametru
    fiind link-ul filmului. In cazul in care nu exista filme in baza de date, afiseaza mesajul "lista e goala".
    :param:
    :return:
    """
    my_cursor = my_db.cursor()
    task = 'select nr_episodes, link, id, snoozed title from tvseries_and_score'
    my_cursor.execute(task)
    result_set = my_cursor.fetchall()
    if len(result_set) != 0:
        for result in result_set:
            if result[3] == "nu":
                request = requests.get(result[1])
                if request.status_code == 200:  # iau fiecare link si verific daca e valid
                    url = get(result[1])
                    request = url.text
                    pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', request).span()[1]
                    pos_sf_nr_ep = re.search('episodes</span>', request).span()[0] - 1  # am eliminat spatiul de dupa nr
                    nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
                    if int(nr_of_ep) == int(
                            result[0]):  # verificam daca e acelasi nr de episoade ca cele din baza de date
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
                print('nimic nou')
    else:
        print('lista e goala')


def youtube(s):
    """
    Extrege din parametrul primit cuvintele ce reprezinta stringul de cautare in variabila target si cauta continutul
    pe YouTube. Intoarce rezultatul sub forma unui json si il converteste intr-un dictionar din care selecteaza si
    afiseaza numai link-ul primului rezultat gasit.
    :param s:
    :return:
    """
    target = s[3:len(s)]
    search = SearchVideos(target, offset=1, mode="json", max_results=20)
    if search.result() is not None:
        dict_search = json.loads(search.result())
        print(dict_search)
        print(dict_search['search_result'][0]['link'])
    else:
        print('nu exista videoclipuri pentru aceasta cautare')


def execute_command(command):
    """
    Verifica daca parametrul primit la intrare reprezinta in intregime sau partial o comanda ce poate fi data de
    utilizator de la tastatura. Daca nu se potriveste cu nicio optiune, afiseaza mesajul "nu e buna comanda". Daca se
    potriveste apeleaza fuctia responsabila cu gestionarea instructiunii primite.
    :param command:
    :return:
    """
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
    elif command == 'suggestions':
        suggestions()
    elif command == 'instructions':
        instructions()
    elif command == 'news':
        news()
    elif command[0:2] == 'yt':
        youtube(command)
    elif command == 'quit':
        sys.exit()
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
