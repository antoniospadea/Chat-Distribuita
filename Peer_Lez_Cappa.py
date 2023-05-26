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
    def __init__(self, nick,ip, port):
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.neighbor_list = {}
        self.oracle_address = ('127.0.0.1', 9999)

        # Inizializza i socket per le diverse comunicazioni
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.neighbor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.oracle_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Collega i socket alle rispettive porte
        self.peer_socket.bind((self.ip, self.port))
        self.neighbor_socket.bind((self.ip, self.port + 1))
        self.oracle_socket.bind((self.ip, self.port + 2))

        # Avvia i thread per le diverse comunicazioni

        print(f"Peer inizializzato: IP={self.ip}, Porta={self.port}")
        print(f"Peer in ascolto su Porta Peer={self.port}, Porta Neighbor={self.port + 1}, Porta Oracle={self.port + 2}")


    # Iniziamo prima con la registrazione all'oracolo mediante il protocollo UDP
    def register_with_oracle(self):
        # Invio del messaggio di registrazione
        registration_data = f"{self.nickname}"
        self.oracle_socket.sendto(registration_data.encode(), self.oracle_address)
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
