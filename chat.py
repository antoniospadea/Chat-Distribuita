from registration import connection
from query import *
import time
from setup import *
from crypto import *
from interface import *


def get_nick(peer):
    """
    La funzione fa inserire da terminale un nickname:
        1. nick è uguale a "-d" il peer si disconnette
        2. nick è uguale a "-l" viene visualizzata la lista dei vicini
        3. nick è una stringa valida la stringa viene resa una stringa maiuscola
    
    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.

    Returns
    -------
    ritorna la stringa del nickname in maiuscolo.

    """
    while True:
        time.sleep(0.2)
        nick = input("Inserisci il nickname del peer a cui vuoi inviare il messaggio:")
        if nick == '-d':
            connection(peer, nick)
            exit()
        elif nick == '-l':
            print_list(peer.neighbor_list)
            continue
        elif nick.upper() == peer.nickname:
            msg = "Non puoi inviare messaggi a te stesso, inserisci un nuovo nickname:"
            print_red(msg)
            continue
        else:
            return nick.upper()


def get_address(peer, nick):
    """
    La funzione restituisce l'address del nickname cercato dal peer

    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.
    nick : stringa del nickname di cui si vuole avere l'address.

    Returns
    -------
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    if nick in peer.neighbor_list.keys():
        address = (peer.neighbor_list[nick][0], peer.neighbor_list[nick][1], peer.neighbor_list[nick][2])
    else:
        ip, port, key = send_query(peer, nick)
        if ip is not None and port is not None and key is not None:
            address = (ip, int(port), key)
        else:
            address = (ip, port, key)
    return address


def sending(peer, message, address):
    """
    La funzione concatena al nickname del peer il messaggio da inviare lo 
    cripta e lo invia al peer destinatario tramite la socket peer_socket

    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.
    message : stringa
        messaggio che si vuole inviare
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    message = f"{peer.nickname}***{message}"
    message = crypt(message, address[2])
    try:
        peer.peer_socket.sendto(message, address[0:2])
    except ConnectionResetError:
        print_red("Peer non raggiungibile")
    start_time = time.time()
    while not peer.ack:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 2:
            print_red("Timeout")
            break


def receive_ack(peer, message, address):
    """
    La funzione imposta l'attributo di peer a True. Tale attributo serve a
    confermare che il messaggio inviato è stato ricevuto dal destinatario.
    Se il nickname non è presente nei suoi vicini se lo salva
    

    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.
    message : stringa
        stringa contentenete il tag '-ack' e il nickname del peer
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    peer.ack = True
    nick = message.split('-ack')[1]
    if nick not in peer.neighbor_list.keys():
        key = ask_key(peer, nick)
        peer.neighbor_list[nick] = (address[0], address[1], key)
        print_green(f"Nuovo vicino registrato: {nick} ({address[0]},{address[1]})")


def send_ack(peer, address, key):
    """
    La funzione invia stringa criptata con la chiave (key), contentenete il tag 
    '-ack' e il nickname del peer che invia l'ack, all'address del peer a cui si
    vuole inviare la stringa
    

    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica
    key : stringa della chiave

    """
    ack = f"-ack{peer.nickname}"
    ack = crypt(ack, key)
    peer.peer_socket.sendto(ack, address[0:2])


def receiving(peer, message, address):
    """
    La funzione si occupa di gestire la ricezione dei messaggi, siano essi 
    ack (inziano con il tag '-ack') o veri e propri messaggi. Nel caso degli
    ack avvia la funzione receive_ack. Nel caso dei messaggi, dopo aver chiesto
    le informazione del nickname ed essersele salvate, visualizza sul terminale
    il mittente e il messaggio.

    Parameters
    ----------
    peer : peer è un'istanza della classe Peer.
    message : stringa
        stringa formata dal nickname del mittente e il messaggio
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    message = decrypt(message, peer.private_key)
    if message.startswith('-ack'):
        receive_ack(peer, message, address)
    else:
        nick, message = message.split('***')
        if nick in peer.neighbor_list.keys():
            message_invertito1 = f"\n{blank}Messaggio ricevuto da " + nick + ": "
            print_risposta(message_invertito1)
            print_risposta(message)
            send_ack(peer, address, peer.neighbor_list[nick][2])
        else:
            key = ask_key(peer, nick)
            if key is None:
                print_red("Ricevuto messaggio da un peer non riconosciuto")
            elif key is not None:
                peer.neighbor_list[nick] = (address[0], address[1], key)
                print_green(f"\nNuovo vicino registrato: {nick} ({address[0]},{address[1]})")
                message_invertito1 = f"\n{blank}Messaggio ricevuto da " + nick + ": "
                print_risposta(message_invertito1)
                print_risposta(message)
                send_ack(peer, address, key)
