import time
import threading


# pe de-o parte cu ajutorul unui thread o data la 5 secunde o sa verific daca datele luate cu ajutorul linkurilor difera fata de datele din baza de date
class TheUpdate(threading.Thread):
    def restart(self):
        self.my_timer = time.time() + 5

    def run(self, *args):
        self.restart()
        while 1:
            if time.time() >= self.my_timer:
                print("a expirat timpul")
                # aici fac verificarile de update
                self.restart()  # resetez timpul


t = TheUpdate()
t.start()
# pe de alta parte iau comenzile date de la tastatura si le prelucrez
while 1:
    x = input()
    # aici introduc comenzile de la tastatura
    print('\nYou entered %r\n' % x)
    t.restart()
