# Nuovo tentativo di costruzione di una classe Peer per la mia rete p2p, iniziamo con una progettazione di massima:
# Il peer viene generato con un ip e una porta (selezionata randomicamente come un intero tra 1000 e 5000), e con un nickname
# che viene richiesto all'utente. Una volta fatto ciò, il peer cerca di registrarsi all'oracolo, che è sempre posto all'indirizzo
# 127.0.0.1 e porta 9999, e che è unico per tutta la rete p2p. Allora invierà all'oracolo il suo nickname, cosi l'oracolo potrà ottenere
# il nick dal messaggio e ip e porta dal socket da cui è stato inviato il messaggio, e registrarli in un dizionario, usando il nick
# come chiave e ip e porta come valore.

import socket
from random import randint
from threading import Thread
import time


class Peer:
    def __init__(self, nick, ip, port):
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.neighbor_list = {}
        self.oracle_registr = ('127.0.0.1', 9999)

        # Inizializza i socket per le diverse comunicazioni
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.neighbor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.oracle_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Imposta l'opzione per riutilizzare la porta
        self.peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.neighbor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.oracle_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Collega i socket alle rispettive porte
        self.peer_socket.bind((self.ip, self.port))
        self.neighbor_socket.bind((self.ip, self.port + 1))
        self.oracle_socket.bind((self.ip, self.port + 2))

        self.SM = Thread(target=self.send_message)
        self.RM = Thread(target=self.receive_message)
        self.RQ = Thread(target=self.receive_query)

        # Avvia i thread per le diverse comunicazioni

        print(f"Peer inizializzato: IP={self.ip}, Porta={self.port}")
        self.register_with_oracle()
        print(
            f"Peer in ascolto su Porta Peer={self.port}, Porta Neighbor={self.port + 1}, Porta Oracle={self.port + 2}")
        self.start_threads()

    # Iniziamo prima con la registrazione all'oracolo mediante il protocollo UDP
    def register_with_oracle(self):
        # Invio del messaggio di registrazione
        registration_data = f"-r {self.nickname}"
        self.oracle_socket.sendto(registration_data.encode(), self.oracle_registr)
        # Ricezione della risposta
        # Se la risposta è positiva, allora l'oracolo ha registrato il peer e lo ha aggiunto alla sua lista di peer registrati
        # altrimenti mi richiederà un nuovo nickname e io reinvierò il messaggio di registrazione
        response, oracle_address = self.oracle_socket.recvfrom(1024)
        response = response.decode()
        if response == f"Registrazione di {self.nickname} avvenuta con successo":
            print(response)
        elif response == f"{self.nickname} non disponibile":
            print(response)
            self.nickname = input("Inserisci un nuovo nickname: ")
            self.register_with_oracle()

    # Implementiamo un thread per l'invio dei messaggi sulla socket peer_socket
    def send_message(self):
        while True:
            nick = input("Inserisci il nickname del peer a cui vuoi inviare il messaggio:")
            # Va controllato che il nickname sia presente nella lista dei vicini, altrimenti si richiama un metodo
            # per interrogare vicini e in casi estremi l'oracolo per riceverlo
            if nick in self.neighbor_list.keys():
                message = input("Inserisci il messaggio da inviare: ")
                self.peer_socket.sendto(message.encode(), (self.neighbor_list[nick][0], self.neighbor_list[nick][1]))
            else:
                # Richiamo il metodo per interrogare
                ip, port = self.send_query(nick)
                if ip is None and port is None:
                    print('Peer non trovato')
                    continue
                else:
                    message = input("Inserisci il messaggio da inviare: ")
                    self.peer_socket.sendto(message.encode(), (ip, int(port)))

    # Implementare il metodo per interrogare i vicini e l'oracolo
    def send_query(self, nick):
        query_data = f"-q {nick}"
        for neighbor in self.neighbor_list.values():
            self.neighbor_socket.sendto(query_data.encode(), neighbor)
            response, neighbor_address = self.neighbor_socket.recvfrom(1024)
            response = response.decode()
            if response == f"-n":
                # passa al vicino successivo
                continue
            else:
                # il vicino ha trovato il peer e mi ha restituito ip e porta che posso restituire al metodo send_message
                ip = response.split(':')[1]
                port = response.split(':')[2]
                return ip, port
        # Se il peer non è stato trovato dai vicini, allora lo cerco nell'oracolo
        self.oracle_socket.sendto(query_data.encode(), self.oracle_registr)
        response, oracle_address = self.oracle_socket.recvfrom(1024)
        response = response.decode()
        if response == f"-n":
            # Il peer non è stato trovato neanche dall'oracolo
            return None, None
        else:
            # Il peer è stato trovato dall'oracolo
            ip = response.split(':')[0]
            port = response.split(':')[1]
            return ip, port

        # Implementiamo invece un metodo per ricevere le query da altri peer (vicini)

    def receive_query(self):
        while True:
            query, neighbor_address = self.neighbor_socket.recvfrom(1024)
            query = query.decode()
            if query.startswith("-q"):
                nick = query.split()[1]
                if nick in self.neighbor_list.keys():
                    # Il peer è presente nella lista dei vicini
                    self.neighbor_socket.sendto(f"{self.neighbor_list[nick][0]} {self.neighbor_list[nick][1]}".encode(),
                                                neighbor_address)
                else:
                    # Il peer non è presente nella lista dei vicini
                    self.neighbor_socket.sendto("-n".encode(), neighbor_address)
            else:
                # Il messaggio non è una query
                continue

    # Implementiamo un metodo per ricevere i messaggi sulla socket peer_socket
    def receive_message(self):
        while True:
            message, peer_address = self.peer_socket.recvfrom(1024)
            message = message.decode()
            # Voglio che il messaggio lo stampi in una nuova riga, quindi uso \n
            print(f"\nMessaggio ricevuto da {peer_address}: {message}")

    # Serve adesso un metodo per gestire il caso in cui l'oracolo ci comunichi che dobbiamo diventare noi oracoli
    def become_oracle(self):
        # DA COMPLETARE
        pass

    # Implementiamo un metodo che fa partire tutti i thread necessari
    def start_threads(self):
        self.SM.start()
        self.RM.start()
        self.RQ.start()


# Creiamo un peer per testare il funzionamento della classe
# Esempio di utilizzo della classe Peer
ip = 'localhost'  # Modifica con l'indirizzo IP del tuo peer
port = randint(1000, 5000)  # Modifica con la porta del tuo peer
nick = input("Inserisci il tuo nickname: ")
peer = Peer(nick, ip, port)
