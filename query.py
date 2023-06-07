import socket

#####################################  FUNZIONI QUERY ORACLE          #################################################


def peer_query(socket, list, message, address):
    """
    La funzione prende message e lo invia alla socket

    Parameters
    ----------
    socket : socket a cui si vuole inviare il messagge
    list : lista in cui si vuole cercare il messagge
    message : stringa che contiene il tag '-q' e il nickname
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica
    """
    query_nick = message.split('-q')[1]
    if query_nick in list.keys():
        response = f"{list[query_nick][0]}:{list[query_nick][1]}:{list[query_nick][2]}"
        socket.sendto(response.encode(), address)
    else:
        response = f"-n"
        socket.sendto(response.encode(), address)


def give_key(socket, list, message, address):
    """
    La funzione invia alla socket la chiave del nickname che si trova nella 
    lista

    Parameters
    ----------
    socket : socket a cui si vuole inviare la chiave
    list : lista in cui si vuole cercare la chiave
    message : stringa che contiene il tag '-k' e il nickname
    address : tupla di 3 elementi:
        1. stringa dell'indirizzo ip
        2. numero intero della porta 
        3. la stringa della chiave pubblica

    """
    query_nick = message.split('-k')[1]
    if query_nick in list.keys():
        response = f"-k{list[query_nick][2]}"
        socket.sendto(response.encode(), address)
    else:
        response = f"-n"
        socket.sendto(response.encode(), address)


#####################################  FUNZIONI QUERY PEER  ###################################################

def query_neighbors(peer, query_data):
    """
    La funzione cerca l'indirizzo tra i vicini del peer

    Parameters
    ----------
    peer : è un'istanza
    query_data : è una stringa contenente il tag '-q' e il nickname

    Returns
    -------
    l'ip, la porta e la chiave che si sta cercando

    """
    for neighbor in peer.neighbor_list.values():
        peer.query_socket.sendto(query_data.encode(), (neighbor[0], neighbor[1] + 1))
        peer.query_socket.settimeout(2)
        try:
            response, neighbor_address = peer.query_socket.recvfrom(2048)
        except socket.timeout:
            continue
        except ConnectionResetError:
            continue
        response = response.decode()
        if response == f"-n":
            continue
        elif response.startswith("-q"):
            # il vicino ha trovato il peer e mi ha restituito ip e porta che posso restituire al metodo send_message
            ip = response.split(':')[1]
            port = response.split(':')[2]
            key = response.split(':')[3]
            return ip, port, key
    return None, None, None


def query_oracle(peer, query_data):
    """
    La funzione chiede l'indirizzo all'oracolo

    Parameters
    ----------
    peer : è un'istanza
    query_data : è una stringa contenente il tag '-q' e il nickname

    Returns
    -------
    l'ip, la porta e la chiave che si sta cercando
    """
    for oracle in peer.oracle_ports:
        try:
            oracle = ('127.0.0.1', oracle - 2)
            peer.oracle_socket.sendto(query_data.encode(), oracle)
            response, oracle_address = peer.oracle_socket.recvfrom(2048)
            response = response.decode()
            if response == f"-n":
                return None, None, None
            else:
                # Il peer è stato trovato dall'oracolo
                ip = response.split(':')[0]
                port = response.split(':')[1]
                key = response.split(':')[2]
                return ip, port, key
        except ConnectionResetError:
            continue


def send_query(peer, nick):
    """
    La funzione restituisce l'indirizzo del nick che si sta cercando

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    nick : stringa

    Returns
    -------
    l'ip, la porta e la chiave che si sta cercando.

    """
    query_data = f"-q{nick}"
    ip, port, key = query_neighbors(peer, query_data)
    if ip is None and port is None and key is None:
        ip, port, key = query_oracle(peer, query_data)
    return ip, port, key


# Creiamo un metodo che ci permetta di chiedere all'oracolo la chiave pubblica di un peer dato il suo nick
def ask_key(peer, nick):
    """
    La funzione riceve dalla socket la chiave del nickname 

    Parameters
    ----------
    peer : è un'istanza della classe Peer
    nick : la stringa del nickname di cui si vuole avere la chiave

    Returns
    -------
    key : chiave pubblica

    """
    query_data = f"-k{nick}"
    for oracle in peer.oracle_ports:
        try:
            oracle = ('127.0.0.1', oracle - 2)
            peer.oracle_socket.sendto(query_data.encode(), oracle)
            response, oracle_address = peer.oracle_socket.recvfrom(2048)
            response = response.decode()
            if response == f"-n":
                return None
            else:
                key = response.split('-k')[1]
                return key
        except ConnectionResetError:
            continue
