from random import randint, choice
from chat import *
from registration import *
from crypto import *


class Peer:
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
        while True:
                try:
                    message, peer_address = self.peer_socket.recvfrom(2048)
                    receiving(self, message, peer_address)
                except ConnectionResetError:
                    print_red("\nPeer non raggiungibile")
                    continue

    def become_oracle(self):
        pass

        # DA COMPLETARE
    def threading(self):
        print(f"Peer inizializzato: IP=\033[1;33m{self.ip}\033[0m, Porta=\033[1;33m{self.port}\033[0m")
        thread_setup(self.receive_query)
        thread_setup(self.receive_message)
        thread_setup(self.send_message)




ip = 'localhost'
port = randint(1000, 5000)
oracle_port = choice([9999, 9996, 9993])
nick = interface_Peer()
peer = Peer(nick, ip, port, oracle_port)
