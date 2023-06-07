import random
import json
from communication import send_registration, send_disconnection
from setup import print_list
from interface import *

#####################################  FUNZIONI REGISTRAZIONE ORACOLO  #################################################

def check_nickname(oracle, nick, address):
    """
    La funzione controlla se il nickname è già presente nella lista dei peer
    dell'oracolo

    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.
    nick : stringa del nickname da controllare
    aaddress : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. chiave pubblica

    Returns
    -------
    nick : stringa del nickname controllata

    """
    if nick in oracle.peer_list.keys():
        response = f"-n{nick} già utilizzato, scegliere un altro nickname"
        oracle.registr_socket.sendto(response.encode(), address)
        return None
    else:
        return nick


def generate_neighbors(oracle):
    """
    La funzione genera la lista dei vicini usando il dizionario peer_list e la 
    libreria json
    
    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.

    Returns
    -------
    neighbors : lista dei vicini

    """
    random_keys = random.sample(list(oracle.peer_list.keys()), 3)
    random_values = [oracle.peer_list[key] for key in random_keys]
    neighbors = json.dumps(dict(zip(random_keys, random_values)))
    return neighbors


def peer_registration(oracle, message, address):
    """
    La funzione si occupa della registrazione del peer

    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.
    message : stringa contente il tag '-r', il nickname, '-k-' e la chiave pubblica
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    nick, key = message.split('-k-')
    nick = nick[2:]
    nick = check_nickname(oracle, nick, address)
    if nick is not None:
        if len(oracle.peer_list) > 3:
            neighbors = generate_neighbors(oracle)
            response = f"-r{neighbors}"
        else:
            response = f"-pr"
        new_peer = (address[0], address[1] - 2, key)
        oracle.peer_list[nick] = new_peer
        oracle.registr_socket.sendto(response.encode(), address)
        send_registration(oracle, nick, new_peer)
        print_list(oracle.peer_list)


def peer_disconnection(oracle, message, address):
    """
    La funzione si occupa della disconessione del peer

    Parameters
    ----------
    oracle : è un'istanza della classe Oracle1, Oracle2 o Oracle3.
    message : stringa contente il tag '-d' e il nickname
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    nick = message[3:]
    if nick in oracle.peer_list.keys():
        del oracle.peer_list[nick]
        response = f"Deregistrazione di {nick} avvenuta con successo"
        oracle.registr_socket.sendto(response.encode(), address)
        send_disconnection(oracle, nick)
        print_green(f"L'utente {nick} si è disconnesso")
        print_list(oracle.peer_list)


#####################################  FUNZIONI REGISTRAZIONE PEER  ###################################################

def update_neighbors(peer, neighbors):
    """
    La funzione aggiorna i vicini del peer

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    neighbors : lista dei vicini

    """
    neighbors = neighbors.split('-r')[1]
    neighbors = json.loads(neighbors)
    for key in neighbors.keys():
        neighbors[key] = tuple(neighbors[key])
    peer.neighbor_list.update(neighbors)


def register_with_oracle(peer, oracle_port):
    """
    La funzione si occupa della registrazione del peer ad un oracolo

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    oracle_port : numero intero che rappresenta la porta dell'oracolo

    """
    registration_data = f"-r{peer.nickname}-k-{peer.public_key}"
    oracle = ('127.0.0.1', oracle_port)
    peer.oracle_socket.sendto(registration_data.encode(), oracle)
    response, oracle_address = peer.oracle_socket.recvfrom(2048)
    response = response.decode()
    avvio_registrazione_print()
    if response.startswith('-r'):
        update_neighbors(peer, response)
        print_info_stato_Peer(response)
        print_list(peer.neighbor_list)
    elif response == '-pr':
        print_info_stato_Peer(response)
    elif response.startswith('-n'):
        print_red(response.split('-n')[1])
        nick = input("Inserisci un nuovo nickname: ")
        while not nick.isalnum():
            nick = input("Nickname non valido, riprova: (solo lettere e numeri) \n")
        peer.nickname = nick.upper()
        register_with_oracle(peer, oracle_port)


def disconnect_with_oracle(peer, oracle_port):
    """
    La funzione si occupa di inviare la disconnesione del peer da un oracolo
    tramite la socket oracle_socket

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    oracle_port : numero intero che rappresenta la porta dell'oracolo da cui 
                  dsiconnettersi

    """
    disconnection_data = f"-d {peer.nickname}"
    oracle = ('127.0.0.1', oracle_port)
    peer.oracle_socket.sendto(disconnection_data.encode(), oracle)
    response, oracle_address = peer.oracle_socket.recvfrom(2048)
    response = response.decode()
    print(response)


def connection(peer, flag):
    """
    La funzione si occupa di chiamare le funzioni giuste a seconda del tag che
    possono essere '-r' e '-d'

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    flag : stringa contenente il tag

    """
    for port in peer.oracle_ports:
        if flag == '-r':
            try:
                register_with_oracle(peer, port)
                break
            except ConnectionResetError:
                continue
        elif flag == '-d':
            try:
                disconnect_with_oracle(peer, port)
                disconnect_with_neighbours(peer)
                break
            except ConnectionResetError:
                continue
    else:
        print_red("Nessun oracolo disponibile, riprovare più tardi")
        while True:
            choice = input("Premere 1 per riprovare, 2 per uscire: ")
            if choice == '1':
                connection(peer, flag)
                break
            elif choice == '2':
                exit()
            else:
                print_red("Scelta non valida")
                continue


def disconnect_with_neighbours(peer):
    """
    La funzione si occupa di inviare la disconnesione del peer dai suoi vicini
    tramite la socket query_socket

    Parameters
    ----------
    peer : è un'istanza della classe Peer

    """
    for neighbor in peer.neighbor_list.keys():
        disconnection_data = f"-d{peer.nickname}"
        neighbor_address = (peer.neighbor_list[neighbor][0], peer.neighbor_list[neighbor][1] + 1)
        peer.query_socket.sendto(disconnection_data.encode(), neighbor_address)


def delete_neighbor(peer, nickname):
    """
    La funzione si occupa di eliminare un nickname dai vicini del peer

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    nickname : stringa del nickname che si è disconnesso

    """
    nickname = nickname.split('-d')[1]
    if nickname in peer.neighbor_list.keys():
        del peer.neighbor_list[nickname]
        print_green(f"L'utente {nickname} si è disconnesso")
        print_list(peer.neighbor_list)
