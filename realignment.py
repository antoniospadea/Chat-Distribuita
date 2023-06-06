import json
from setup import *

def realignment_ask(oracle):
    """
    La funzione chiede che la lista dei peer venga aggiornata agli altri 
    oracoli tramite la socket communication_socket

    Parameters
    ----------
    oracle : è un'istanza della classe Oracole1, Oracle2 o Oracle3

    """
    other_oracle = [x for x in [9999, 9996, 9993] if x != oracle.port]
    for port in other_oracle:
        try:
            message = f"-l0" 
            oracle.communication_socket.sendto(message.encode(), ('localhost', port - 1))
        except ConnectionResetError:
            continue

def realign(oracle, message=None):
    """
    La funzione aggiorna la lista dei peer e la visualizza sul terminale

    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.
    message : stringa. The default is None.

    """
    l1 = len(oracle.peer_list.keys())
    if message.startswith('-l1'):
        l1 = len(oracle.peer_list.keys())
        message = message.split('-l1')[1]
        message = json.loads(message)
        for key in message.keys():
            message[key] = tuple(message[key])
        oracle.peer_list.update(message)
        l2 = len(oracle.peer_list.keys())
        if l1 != l2:
            print_list(oracle.peer_list)
    else:
        pass



def receive_realignment_request(oracle, address):
    """
    La funzione una volta ricevuta la richiesta di riallineamneto, invia la 
    lista dei peer registrati all'oracolo di cui abbiamo l'address

    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.
    address : tupla di 2 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 

    """    
    try:
        peer_list = json.dumps(oracle.peer_list)
        message = f"-l1{peer_list}"
        oracle.communication_socket.sendto(message.encode(), address)
    except ConnectionResetError:
        pass
