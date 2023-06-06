from random import randint, choice
from chat import *
from registration import *
from crypto import *


class Peer:
    """
        La classe Peer ha come attributi il nickname, l'ip, la porta e l'oracle_port
        Inoltre assegnamo degli attributi quali:
        self.neighbor_list: dizionario che ha come chiave il nickname dei peer 
                            vicini e come valore la tupla di 3 elementi
                            (ip,porta,chiave)
        
        self.oracle_ports: lista delle porte degli oracoli
        
        self.oracle_socket: socekt per la gestione della comunicazione
                                   con l'oracolo
        self.query_socket: socket per la gestione delle query ai peer
        self.peer_socket: socket per la gestione della comunicazione con gli
                          altri peer
                          
        self.ack: attributo per la gestione degli ack
        self.public_key: attributo che si salva la chiave pubblica
        self.private_key: attributo che si salva la chiave privata
        
        Per prima cosa la classe chiama il metodo threading_setup()

        Parameters
        ----------
        nick : stringa contenente il nome del Peer
        ip : stringa contenente l'indirizzo ip
        port : il numero intero della porta
        oracle_port : il numero intero della porta dell'oracle di default

        """
    def __init__(self, nick, ip, port, oracle_port):
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.neighbor_list = {}

        other_oracle = [x for x in [9999, 9996, 9993] if x != oracle_port]
        self.oracle_ports = [oracle_port, other_oracle[0], other_oracle[1]]

        self.ack = False

        self.public_key, self.private_key = keys()

        self.oracle_socket = socket_setup(self.ip, self.port+2)
        self.query_socket = socket_setup(self.ip, self.port+1)
        self.peer_socket = socket_setup(self.ip, self.port)

        connection(self, '-r')
        self.threading()

    def send_message(self):
        """
        Il metodo si occupa dell'invio dei messaggi ai peer
        """
        avvio_chat()
        while True:
                self.ack = False
                nick = get_nick(self)
                address = get_address(self, nick)
                if address == (None, None, None):
                    print_red("Peer non trovato")
                    continue
                message = input("Inserisci il messaggio da inviare: ")
                # controlliamo non siano piu di 100 caratteri altrimenti richiediamo l'inserimento
                while len(message) > 100:
                    print_red("Il messaggio deve essere lungo al massimo 100 caratteri")
                    message = input("Inserisci il messaggio da inviare: ")
                sending(self, message, address)

    def receive_query(self):
        """
        Il metodo si occupa della gestione delle query

        """
        while True:
                try:
                    query, neighbor_address = self.query_socket.recvfrom(2048)
                except ConnectionResetError:
                    # Se il vicino non risponde entro cinque secondi, passo al vicino successivo
                    continue
                except socket.timeout:
                    continue
                query = query.decode()
                if query.startswith("-q"):
                    peer_query(self.query_socket, self.neighbor_list, query, neighbor_address)
                elif query.startswith("-d"):
                    delete_neighbor(self, query)

    def receive_message(self):
        """
        Il metodo si occupa della recezione dei messaggi dei peer

        """
        while True:
                try:
                    message, peer_address = self.peer_socket.recvfrom(2048)
                    receiving(self, message, peer_address)
                except ConnectionResetError:
                    print_red("\nPeer non raggiungibile")
                    continue

    def become_oracle(self):
        """
        Il metodo si occupa di far diventare un peer un oracolo in caso di
        interruzione di uno dei tre oracoli

        """
        pass

        # DA COMPLETARE
    def threading(self):
        """
        Il metodo si occupa di inizializzare i 3 thread

        """
        print(f"Peer inizializzato: IP=\033[1;33m{self.ip}\033[0m, Porta=\033[1;33m{self.port}\033[0m")
        thread_setup(self.receive_query)
        thread_setup(self.receive_message)
        thread_setup(self.send_message)


if __name__ == '__main__':
    """
    Creiamo un peer
    """
    ip = 'localhost'
    port = randint(1000, 5000)
    oracle_port = choice([9999, 9996, 9993])
    nick = interface_Peer()
    peer = Peer(nick, ip, port, oracle_port)
