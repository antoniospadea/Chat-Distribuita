import json
from setup import *

def realignment_ask(oracle):
    other_oracle = [x for x in [9999, 9996, 9993] if x != oracle.port]
    for port in other_oracle:
        try:
            message = f"-l0"  # il tag -l0 serve per richiedere realignment, invece -l1 è il tag per la ricezione
            oracle.communication_socket.sendto(message.encode(), ('localhost', port - 1))
        except ConnectionResetError:
            continue


# Creiamo un metodo che permette a un oracolo di riallinearsi con gli altri oracoli il caso di crash o avvio
# ritardato Questo metodo semplicemente richiede la lista dei peer registrati agli altri oracoli e la aggiunge
# alla propria lista
def realign(oracle, message=None):
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


# Creiamo un metodo che riceve richieste di realignment dagli altri oracoli e restituisce la lista dei peer
# registrati
def receive_realignment_request(oracle, address):
    # Ricevuta la richiesta di realignment, inviamo la lista dei peer registrati all'oracolo di cui abbiamo
    # address
    try:
        # inviamo la lista usando la libreria json
        peer_list = json.dumps(oracle.peer_list)
        message = f"-l1{peer_list}"
        oracle.communication_socket.sendto(message.encode(), address)
    except ConnectionResetError:
        pass
