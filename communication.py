import json
from setup import print_list
from interface import *


def receive_registrations(oracle, message):
    message = message.split('-r')[1]
    message = json.loads(message)
    for key in message.keys():
        message[key] = tuple(message[key])
    oracle.peer_list.update(message)
    print_list(oracle.peer_list)


def receive_disconnections(oracle, message):
    message = message.split('-d')[1]
    del oracle.peer_list[message]
    print_green(f"\nL'utente {message} si è disconnesso")
    print_list(oracle.peer_list)


def send_registration(oracle, nick, peer):
    other_oracle = [x for x in [9999, 9996, 9993] if x != oracle.port]
    new_peer = {nick: (peer[0], peer[1], peer[2])}
    # Trasformiamo il dizionario in una stringa
    new_peer = json.dumps(new_peer)
    for port in other_oracle:
        try:
            message = f"-r{new_peer}"
            oracle.communication_socket.sendto(message.encode(), ('localhost', port - 1))
        except ConnectionResetError:
            pass


def send_disconnection(oracle, nick):
    other_oracle = [x for x in [9999, 9996, 9993] if x != oracle.port]
    for port in other_oracle:
        try:
            message = f"-d{nick}"
            oracle.communication_socket.sendto(message.encode(), ('localhost', port - 1))
        except ConnectionResetError:
            pass
