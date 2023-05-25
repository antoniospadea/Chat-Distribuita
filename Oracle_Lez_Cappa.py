# In questo file invece creiamo la classe Oracolo posta all'indirizzo 127.0.0.1 e porta 9999, che è unico per tutta la rete p2p.
# e costruiamo la funzione peer_communication che si occupa di ricevere le richieste di registrazione da parte dei peer

import socket
from threading import Thread


class Oracle:
    def __init__(self, nick, ip, port):
        self.peer_list = {}
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.oracle_address = (self.ip, self.port)

        # Inizializza il socket per le diverse comunicazioni
        self.oracle_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.oracle_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Collega il socket alla porta
        self.oracle_socket.bind(self.oracle_address)

        # Avvia il thread per le diverse comunicazioni
        self.oracle_thread = Thread(target=self.peer_registration)

        self.oracle_thread.start()

        print(f"Oracolo inizializzato: IP={self.ip}, Porta={self.port}")

    # Definiamo il metodo per ricevere le richieste di registrazione da parte dei peer
    def peer_registration(self):
        while True:
            # Ricevi il messaggio dal Peer
            message, address = self.oracle_socket.recvfrom(1024)
            message = message.decode()
            print(f"Richiesta di registrazione da parte di {message}")

            # Aggiungi il Peer alla lista dei Peer registrati solo se non è già presente o se quel nickname è già stato registrato da un altro peer
            # basta vedere se nick è una delle chiavi del dizionario peer_list
            if message not in self.peer_list.keys():
                self.peer_list[message] = address
                # Invia la conferma di registrazione al Peer
                response = f"Registrazione di {message} avvenuta con successo"
                self.oracle_socket.sendto(response.encode(), address)
                print(f"Lista dei Peer registrati: {self.peer_list}")
            else:
                response = f"{message} non disponibile"
                self.oracle_socket.sendto(response.encode(), address)
