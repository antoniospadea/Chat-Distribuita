# In questo file invece creiamo la classe Oracolo posta all'indirizzo 127.0.0.1 e porta 9999, che è unico per tutta la rete p2p.
# e costruiamo la funzione peer_communication che si occupa di ricevere le richieste di registrazione da parte dei peer

import socket
from threading import Thread
import random
import json

class Oracle:
    def __init__(self, nick, ip, port):
        self.peer_list = {}
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.oracle_registr = (self.ip, self.port)
        self.oracle_query = (self.ip, 9998)

        # Inizializza il socket per le diverse comunicazioni
        self.registr_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Imposta l'opzione per riutilizzare la porta
        self.registr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Collega il socket alla porta
        self.registr_socket.bind((self.ip, self.port))

        print(f"Oracolo inizializzato: IP={self.ip}, Porta={self.port}")

        # Avvia il thread per le diverse comunicazioni
        self.registr_thread = Thread(target=self.receive_message())
        self.registr_thread.start()


    # Definiamo il metodo per ricevere le richieste di registrazione da parte dei peer
    def peer_registration(self,message,address):
        # Aggiungi il Peer alla lista dei Peer registrati solo se non è già presente o se quel nickname è già stato registrato da un altro peer
        # basta vedere se nick è una delle chiavi del dizionario peer_list
        if message.startswith('-r'):
            message = message[3:]
            if message not in self.peer_list.keys():
                # Voglio anche inviare 3 peer random al peer che si è registrato cosi che possa inserirli nella sua lista dei vicini
                # Devo passare sia il nickname (che è la chiave del dizionario) che l'indirizzo e la porta (che è il valore del dizionario)
                # Per fare questo devo prima creare una lista di chiavi e poi estrarre tre chiavi random
                # Questo va fatto se però la lista dei peer registrati è maggiore di tre
                if len(self.peer_list) > 3:
                    # Creo la lista dei vicini usando il dizionario peer_list e la libreria json
                    # Estraggo 3 chiavi random
                    random_keys = random.sample(list(self.peer_list.keys()), 3)
                    # Estraggo i valori corrispondenti alle chiavi
                    random_values = [self.peer_list[key] for key in random_keys]
                    # Creo la lista dei vicini in modo che sia facile da ricevere dal Peer
                    neighbors = json.dumps(dict(zip(random_keys, random_values)))
                    # Salviamo la porta ma -2
                    peer = (address[0], address[1]-2)
                    self.peer_list[message] = peer
                    # Invia i vicini al Peer con davanti il tag -d (done) cosi che sappia che la registrazione è andata a buon fine
                    response = f"-d{neighbors}"
                    self.registr_socket.sendto(response.encode(), address)
                    print(f"Lista dei Peer registrati: {self.peer_list}")
                else:
                    # invio solo il messaggio di conferma
                    peer = (address[0], address[1]-2)
                    self.peer_list[message] = peer
                    # Invia il tag -pd (partially done) cosi che sappia che la registrazione è andata a buon fine
                    response = f"-pd"
                    self.registr_socket.sendto(response.encode(), address)
                    print(f"Lista dei Peer registrati: {self.peer_list}")
            else:
                response = f"{message} non disponibile"
                self.registr_socket.sendto(response.encode(), address)
        elif message.startswith('-d'):
            message = message[3:]
            # Controlla se il nickname è presente nella lista dei Peer registrati e in caso eliminalo
            if message in self.peer_list.keys():
                del self.peer_list[message]
                # Invia la conferma di deregistrazione al Peer
                response = f"Deregistrazione di {message} avvenuta con successo"
                self.registr_socket.sendto(response.encode(), address)
                print(f"Lista dei Peer registrati: {self.peer_list}")

    # Definisce il metodo per ricevere le richieste di query da parte dei peer
    def peer_query(self, message, address):
        if message in self.peer_list.keys():
            # Invia la conferma di registrazione al Peer
            response = f"{self.peer_list[message][0]}:{self.peer_list[message][1]}"
            self.registr_socket.sendto(response.encode(), address)
        else:
            response = f"-n"
            self.registr_socket.sendto(response.encode(), address)


        # Metodo che riceve i messaggi, e che richiama la funzione giusta a seconda del tag del messaggio ricevuto
    def receive_message(self):
        while True:
            # Ricevi il messaggio dal Peer
            message, address = self.registr_socket.recvfrom(1024)
            message = message.decode()
            if message.startswith('-q'):
                message = message[3:]
                self.peer_query(message, address)
            elif message.startswith('-r'):
                self.peer_registration(message,address)
            elif message.startswith('-d'):
                self.peer_registration(message,address)
            else:
                pass



# Creiamo un Oracolo per testare il funzionamento della classe
if __name__ == '__main__':
    ip = 'localhost'
    port = 9999
    nick = 'Oracle1'
    oracle = Oracle(nick, ip, port)
