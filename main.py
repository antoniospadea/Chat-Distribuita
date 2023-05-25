from Oracle_Lez_Cappa import Oracle
from Peer_Lez_Cappa import Peer
import socket
from random import randint
from threading import Thread
import time

if __name__ == '__main__':
    ip = 'localhost'
    port1 = 9999
    nick1 = 'primo_oracolo'
    oracle1 = Oracle(nick1, ip, port1)

    port2 = 9998
    nick2 = 'secondo_oracolo'
    oracle2 = Oracle(nick2, ip, port2)

    port3 = 9997
    nick3 = 'terzo_oracolo'
    oracle3 = Oracle(nick3, ip, port3)

    # Creiamo un peer per testare il funzionamento della classe
    # Esempio di utilizzo della classe Peer
    ip = 'localhost'  # Modifica con l'indirizzo IP del tuo peer
    port = randint(1000,5000)  # Modifica con la porta del tuo peer
    nick = input("Inserisci il tuo nickname: ")
    peer = Peer(nick, ip, port)
    peer.register_with_oracle()

    input("Premi Enter per terminare...")
    