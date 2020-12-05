import re
from requests import get

# from bs4 import BeautifulSoup as Soup

# print(re.search('bc','abc').span()[0],', ',re.search('bc','abc').span()[1])
link = input('introduceti link-ul dorit: ')
nota = input('intoduceti nota: ')
last_episode = input('ultimul episod vizionat: ')
date = input('data ultimei vizionari: ')

url = get(link)
request = url.text

# soup_data = Soup(request, 'html.parser')
# movie = soup_data.find('div', {'class': 'title_wrapper'})
# titlu = movie.h1.text
# print(titlu)  # titlul este in interiorul unui h1

pos_incep_titlu = re.search('<h1 class="">', url.text).span()[1]
pos_sf_titlu = re.search('</h1>', url.text).span()[0] - 18  # eliminam caracterele de la titlu pana la </h1>
title = request[pos_incep_titlu:pos_sf_titlu]
print(title, nota)

pos_incep_nr_ep = re.search('<span class="bp_sub_heading">', url.text).span()[1]
pos_sf_nr_ep = re.search('episodes</span>', url.text).span()[0] - 1  # am eliminat spatiul de dupa nr
nr_of_ep = request[pos_incep_nr_ep:pos_sf_nr_ep]
print(nr_of_ep, 'episoade')
