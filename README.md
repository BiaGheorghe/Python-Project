# Python-Project

Creați un tool care monitorizeaza serialele favorite. Într-o bază de date se va păstra numele
serialului, link către IMDB, ultimul episod vizionat, data ultimei vizionari, un scor ( setat de
user pentru serial ). Cand va fi rulat tool-ul va lista ce seriale noi apărute nu au fost vizionate
în funcție de scorul serialului. Tool-ul va cauta si traler-uri pe youtube sau upload-uri care au
legatura cu un anumit episod dintr-un serial și va oferi o lista a acestora (respectiv notificari
dacă apar altele).
INPUT:
Adaugare serial ( link imdb si scor )
Modificare scor
Modificare data
snooze/unsnooze ( dacă e snoozed un serial nu va apărea în lista de seriale cu episoade noi
)
Listare - va lista toate episoadele noi ale serialelor din db ( mai puțin cele snoozed )
OUTPUT:
Rezultatul comenzilor împreuna cu logarea activităților și erorile apărute
