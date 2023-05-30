# In questo file invece creiamo la classe Oracolo posta all'indirizzo 127.0.0.1 e porta 9999, che è unico per tutta
# la rete p2p. E costruiamo la funzione peer_communication che si occupa di ricevere le richieste di registrazione da
# parte dei peer

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
        # List comprehension per creare la lista degli altri oracoli, bisogna aggiungere le due porte che sono
        # diverse dalla mia ipotizzando di non sapere quale oracolo siamo
        self.other_oracle = [x for x in [9999, 9996, 9993] if x != self.port]

        self.nickname = nick

        # le porte degli oracle possono essere 9999 9996 e 9993, io devo aggiungere a other_oracle le due diverse
        # dalla mia

        # Inizializza il socket per le diverse comunicazioni
        self.registr_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.query_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Imposta l'opzione per riutilizzare la porta
        self.registr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.communication_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.query_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Collega il socket alla porta
        self.registr_socket.bind((self.ip, self.port))
        self.communication_socket.bind((self.ip, self.port - 1))
        self.query_socket.bind((self.ip, self.port - 2))

        print(f"Oracolo inizializzato: IP={self.ip}, Porta={self.port}")


        # Avvia il thread per le diverse comunicazioni
        self.query_thread = Thread(target=self.receive_query)
        self.communication_thread = Thread(target=self.receive_from_oracle)
        self.registr_thread = Thread(target=self.receive_message)

        self.start_threads()
        self.realignement_ask()

    # Definiamo il metodo per ricevere le richieste di registrazione da parte dei peer
    def peer_registration(self, message, address):
        # Aggiungi il Peer alla lista dei Peer registrati solo se non è già presente o se quel nickname è già stato
        # registrato da un altro peer basta vedere se nick è una delle chiavi del dizionario peer_list
        if message.startswith('-r'):
            # il messaggio è composto da -r, poi nickname, poi -k e poi la chiave pubblica, iniziamo ad estrarre il nickname e la chiave in due variabili
            nick, key = message.split('-k')
            nick = nick[2:]
            key = key[1:]
            # Implementiamo un check sui caratteri utilizzati, vogliamo solo Caratteri e Numeri
            if nick.isalnum():
                # Controlla se il nickname è già presente nella lista dei Peer registrati e in caso invia un messaggio di errore
                if nick not in self.peer_list.keys():
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
                        peer = (address[0], address[1] - 2, key)
                        self.peer_list[nick] = peer
                        # Invia i vicini al Peer con davanti il tag -d (done) cosi che sappia che la registrazione è andata a buon fine
                        response = f"-d{neighbors}"
                        self.registr_socket.sendto(response.encode(), address)
                        # Chiamo il metodo per inviare il nuovo peer agli altri Oracle
                        self.send_communication('-r', message, peer)
                        output = ', '.join([f"{key}: ({', '.join(map(str, values[:2]))})" for key, values in self.peer_list.items()])
                        print(f"Lista dei Peer registrati: {output}")
                    else:
                        # invio solo il messaggio di conferma
                        peer = (address[0], address[1] - 2, key)
                        self.peer_list[nick] = peer
                        # Invia il tag -pd (partially done) cosi che sappia che la registrazione è andata a buon fine
                        response = f"-pd"
                        self.registr_socket.sendto(response.encode(), address)
                        # Chiamo il metodo per inviare il nuovo peer agli altri Oracle
                        self.send_communication('-r', message, peer)
                        output = ', '.join([f"{key}: ({', '.join(map(str, values[:2]))})" for key, values in self.peer_list.items()])
                        print(f"Lista dei Peer registrati: {output}")
                else:
                    response = f"-n{message} già utilizzato, scegliere un altro nickname"
                    self.registr_socket.sendto(response.encode(), address)
            else:
                response = f"-nNickname non valido, utilizzare solo caratteri e numeri"
                self.registr_socket.sendto(response.encode(), address)
        elif message.startswith('-d'):
            nick = message[3:]
            # Controlla se il nickname è presente nella lista dei Peer registrati e in caso eliminalo
            if nick in self.peer_list.keys():
                del self.peer_list[nick]
                # Invia la conferma di deregistrazione al Peer
                response = f"Deregistrazione di {nick} avvenuta con successo"
                self.registr_socket.sendto(response.encode(), address)
                self.send_communication('-d',nick)
                print(f"L'utente {nick} si è disconnesso")
                # stampiamo i nick e per ciascuno la porta e l'indirizzo, non possiamo stampare direttamente il dizionario
                # perchè c'è la chiave pubblica che non vogliamo stampare, quindi facciamo un ciclo for
                output = ', '.join([f"{key}: ({', '.join(map(str, values[:2]))})" for key, values in self.peer_list.items()])
                print(f"Lista dei Peer registrati: {output}")

    # Definisce il metodo per ricevere le richieste di query da parte dei peer
    def peer_query(self, message, address):
        # Controlliamo se il nickname è presente nella lista dei Peer registrati e in caso invia un messaggio di errore
        if message in self.peer_list.keys():
            response = f"{self.peer_list[message][0]}:{self.peer_list[message][1]}:{self.peer_list[message][2]}"
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
            if message.startswith('-r'):
                self.peer_registration(message, address)
            elif message.startswith('-d'):
                self.peer_registration(message, address)
            else:
                pass

    def receive_query(self):
        while True:
            # Ricevi il messaggio dal Peer
            message, address = self.query_socket.recvfrom(1024)
            message = message.decode()
            if message.startswith('-q'):
                message = message[3:]
                self.peer_query(message, address)
            else:
                pass

    def receive_communication(self, message, address):
        # Questo metodo serve perchè ogni volta che avviene una registrazione, i tre oracle devono ricevere la lista
        # dei peer registrati e aggiornare la propria lista dei peer registrati
        if message.startswith('-r'):
            message = message.split('-r')[1]
            message = json.loads(message)
            for key in message.keys():
                message[key] = tuple(message[key])
            self.peer_list.update(message)
            print(f"Lista dei Peer registrati: {self.peer_list}")
        elif message.startswith('-d'):
            message = message.split('-d')[1]
            del self.peer_list[message]
            print(f"L'utente {message} si è disconnesso")
            print(f"Lista dei Peer registrati: {self.peer_list}")
        else:
            pass

    def send_communication(self, tag, nick=None, address=None):
        # Se il tag è -r allora invia agli altri oracle
        if tag == '-r':
            # Invia il messaggio agli altri Oracle con davanti il tag -r (registration) cosi che sappiano che è una registrazione
            # Creiamo un dizionario con chiave il nickname e valore l'indirizzo del peer
            new_peer = {nick: address}
            new_peer = json.dumps(new_peer)
            for port in self.other_oracle:
                try:
                    message = f"-r{new_peer}"
                    self.communication_socket.sendto(message.encode(), ('localhost', port - 1))
                except:
                    pass
        # Se il tag è -d allora invia agli altri oracle solo il nickname
        elif tag == '-d':
            # Invia il messaggio agli altri Oracle
            for port in self.other_oracle:
                try:
                    message = f"-d{nick}"
                    self.communication_socket.sendto(message.encode(), ('localhost', port - 1))
                except ConnectionResetError:
                    pass

    def realignement_ask(self):
        for port in self.other_oracle:
            try:
                message = f"-l0"  # il tag -l0 serve per richiedere realignement, invece -l1 è il tag per la ricezione
                self.communication_socket.sendto(message.encode(), ('localhost', port - 1))
            except ConnectionResetError:
                continue

    # Creiamo un metodo che permette ad un oracolo di riallinearsi con gli altri oracoli il caso di crash o avvio ritardato
    # Questo metodo semplicemente richiede la lista dei peer registrati agli altri oracoli e la aggiunge alla propria lista
    def realign(self, message=None, address=None):
        l1 = len(self.peer_list.keys())
        if message.startswith('-l1'):
            l1 = len(self.peer_list.keys())
            message = message.split('-l1')[1]
            message = json.loads(message)
            for key in message.keys():
                message[key] = tuple(message[key])
            self.peer_list.update(message)
            l2 = len(self.peer_list.keys())
            if l1 != l2:
                print(f"Lista dei Peer registrati: {self.peer_list}")
        else:
            pass

    # Creiamo un metodo che riceve richieste di realignment dagli altri oracoli e restituisce la lista dei peer
    # registrati
    def receive_realignment_request(self, address):
        # Ricevuta la richiesta di realignement, inviamo la lista dei peer registrati all'oracolo di cui abbiamo
        # l'address
        try:
            # inviamo la lista usando la libreria json
            peer_list = json.dumps(self.peer_list)
            message = f"-l1{peer_list}"
            self.communication_socket.sendto(message.encode(), address)
        except ConnectionResetError:
            pass

    # Creiamo un metodo che permette di ricevere comunicazioni tra oracle e poi le smista al metodo giusto
    def receive_from_oracle(self):
        while True:
            # Ricevi il messaggio da un Oracle
            try:
                message, address = self.communication_socket.recvfrom(1024)
                message = message.decode()
                if message.startswith('-r'):
                    self.receive_communication(message, address)
                elif message.startswith('-d'):
                    self.receive_communication(message, address)
                elif message.startswith('-l0'):
                    self.receive_realignment_request(address)
                elif message.startswith('-l1'):
                    self.realign(message, address)
            except ConnectionResetError:
                pass

    def start_threads(self):
        self.registr_thread.start()
        self.query_thread.start()
        self.communication_thread.start()


# Creiamo un Oracolo per testare il funzionamento della classe
if __name__ == '__main__':
    ip = 'localhost'
    port = 9999
    nick = 'Oracle1'
    oracle = Oracle(nick, ip, port)
