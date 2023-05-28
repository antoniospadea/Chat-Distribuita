# Nuovo tentativo di costruzione di una classe Peer per la mia rete p2p, iniziamo con una progettazione di massima:
# Il peer viene generato con un ip e una porta (selezionata in modo casuale come un intero tra 1000 e 5000),
# e con un nickname che viene richiesto all'utente. Una volta fatto ciò, il peer cerca di registrarsi all'oracolo,
# che è sempre posto all'indirizzo 127.0.0.1 e porta 9999, e che è unico per tutta la rete p2p. Allora invierà
# all'oracolo il suo nickname, cosi l'oracolo potrà ottenere il nick dal messaggio e ip e porta dal socket da cui è
# stato inviato il messaggio, e registrarli in un dizionario, usando il nick come chiave e ip e porta come valore.

import socket
from random import randint, choice
from threading import Thread
import json


class Peer:
    def __init__(self, nick, ip, port, oracle_port):
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick
        self.neighbor_list = {}
        self.oracle_registr = ('127.0.0.1', oracle_port)
        self.oracle_query = ('127.0.0.1', oracle_port - 2)
        other_oracle = [x for x in [9999, 9996, 9993] if x != oracle_port]
        self.oracle_ports = [oracle_port, other_oracle[0], other_oracle[1]]

        # Inizializza i socket per le diverse comunicazioni
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.neighbor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.oracle_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Imposta l'opzione per riutilizzare la porta
        self.peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.neighbor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.oracle_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Collega i socket alle rispettive porte
        self.peer_socket.bind((self.ip, self.port))
        self.neighbor_socket.bind((self.ip, self.port + 1))
        self.oracle_socket.bind((self.ip, self.port + 2))

        self.SM = Thread(target=self.send_message)  # RICORDA DI NON METTERE LE PARENTESI DOPO IL NOME DEL METODO
        self.RM = Thread(target=self.receive_message)
        self.RQ = Thread(target=self.receive_query)

        # Avvia i thread per le diverse comunicazioni

        self.registration()
        print(f"Peer inizializzato: IP=\033[1;33m{self.ip}\033[0m, Porta=\033[1;33m{self.port}\033[0m")

        self.start_threads()

    # Iniziamo prima con la registrazione all'oracolo mediante il protocollo UDP
    def register_with_oracle(self, oracle_port):
        # Invio del messaggio di registrazione Inseriamo un controllo in caso di timeout nella risposta o di
        # connessione rifiutata, in tal caso passiamo all'oracolo successivo
        registration_data = f"-r {self.nickname}"
        oracle = ('127.0.0.1', oracle_port)
        self.oracle_socket.sendto(registration_data.encode(), oracle)
        # Ricezione della risposta Se la risposta è positiva, allora l'oracolo ha registrato il peer e lo ha aggiunto
        # alla sua lista di peer registrati altrimenti mi richiederà un nuovo nickname e lo re invierò il messaggio di
        # registrazione
        response, oracle_address = self.oracle_socket.recvfrom(1024)
        response = response.decode()
        # Se tutto è andato a buon fine, l'oracolo potrà scrivermi o il tag -d seguito dai dati dei vicini,
        # oppure il tag -pd senza vicini oppure un messaggio se il nickname è già presente nella rete
        if response.startswith('-d'):
            # Va gestito il passaggio dei vicini del messaggio al dizionario dei vicini
            # la risposta è un tag -d e poi un json con i vicini
            response = response.split('-d')[1]
            # Dobbiamo però salvare questi vicini nel dizionario avendo i valori come tuple non liste
            response = json.loads(response)
            for key in response.keys():
                response[key] = tuple(response[key])
            self.neighbor_list.update(response)
            print("Registrazione completata con successo")
            # Stampo la lista dei vicini
            print(f"Lista dei Vicini: \033[1;33m{self.neighbor_list}\033[0m")
        elif response == '-pd':
            print("Registrazione completata con successo, nessun vicino disponibile")
        elif response.startswith('-n'):
            print(response.split('-n')[1])
            self.nickname = input("Inserisci un nuovo nickname: ")
            self.register_with_oracle(oracle_port)

    # Implementiamo un thread per l'invio dei messaggi sulla socket peer_socket
    def send_message(self):
        while True:
            nick = input("Inserisci il nickname del peer a cui vuoi inviare il messaggio:")
            # Va controllato che il nickname sia presente nella lista dei vicini, altrimenti si richiama un metodo
            # per interrogare vicini e in casi estremi l'oracolo per riceverlo
            if nick in self.neighbor_list.keys():
                message = input("Inserisci il messaggio da inviare: ")
                # Voglio inviare all'inizio anche il mio nick, cosicché chi lo riceve possa registrarlo tra i suoi
                # vicini e possa rispondere, tra il nick e il messaggio metto un separatore (-s-)
                message = f"{self.nickname}-s-{message}"
                self.peer_socket.sendto(message.encode(), (self.neighbor_list[nick][0], self.neighbor_list[nick][1]))
            else:
                # Richiamo il metodo per interrogare
                ip, port = self.send_query(nick)
                if ip is None and port is None:
                    print('Peer non trovato')
                    continue
                else:
                    message = input("Inserisci il messaggio da inviare: ")
                    message = f"{self.nickname}-s-{message}"
                    try:
                        self.peer_socket.sendto(message.encode(), (ip, int(port)))
                    except ConnectionResetError:
                        print("Peer non raggiungibile")
                        continue

    # Implementare il metodo per interrogare i vicini e l'oracolo
    def send_query(self, nick):
        query_data = f"-q {nick}"
        for neighbor in self.neighbor_list.values():
            # Invio il messaggio di query al vicino usando la sua porta + 1
            self.neighbor_socket.sendto(query_data.encode(), (neighbor[0], neighbor[1] + 1))
            # Mettiamo un timeout di CINQUE secondi per la risposta
            self.neighbor_socket.settimeout(1)
            # Sarebbe anche il caso di fare un check, se la connessione viene interrotta forzatamente dall host remoto
            # allora bisogna gestire l'eccezione
            try:
                response, neighbor_address = self.neighbor_socket.recvfrom(1024)
            except socket.timeout:
                # Se il vicino non risponde entro cinque secondi, passo al vicino successivo
                continue
            except ConnectionResetError:
                continue
            response = response.decode()
            if response == f"-n":
                # passa al vicino successivo
                continue
            else:
                # il vicino ha trovato il peer e mi ha restituito ip e porta che posso restituire al metodo send_message
                ip = response.split(':')[1]
                port = response.split(':')[2]
                return ip, port
        # Se il peer non è stato trovato dai vicini, allora lo cerco nell'oracolo, partendo dal predefinito
        for oracle in self.oracle_ports:
            try:
                oracle = ('127.0.0.1', oracle - 2)
                self.oracle_socket.sendto(query_data.encode(), oracle)
                response, oracle_address = self.oracle_socket.recvfrom(1024)
                response = response.decode()
                if response == f"-n":
                    # Il peer non è stato trovato neanche dall'oracolo
                    return None, None
                else:
                    # Il peer è stato trovato dall'oracolo
                    ip = response.split(':')[0]
                    port = response.split(':')[1]
                    return ip, port
            except ConnectionResetError:
                continue

        # Implementiamo invece un metodo per ricevere le query da altri peer (vicini)

    def receive_query(self):
        while True:
            try:
                query, neighbor_address = self.neighbor_socket.recvfrom(1024)
            except ConnectionResetError:
                continue
            query = query.decode()
            if query.startswith("-q"):
                nick = query.split()[1]
                if nick in self.neighbor_list.keys():
                    # Il peer è presente nella lista dei vicini
                    self.neighbor_socket.sendto(f"{self.neighbor_list[nick][0]} {self.neighbor_list[nick][1]}".encode(),
                                                neighbor_address)
                else:
                    # Il peer non è presente nella lista dei vicini
                    self.neighbor_socket.sendto("-n".encode(), neighbor_address)
            else:
                # Il messaggio non è una query
                continue

    # Implementiamo un metodo per ricevere i messaggi sulla socket peer_socket
    def receive_message(self):
        while True:
            try:
                message, peer_address = self.peer_socket.recvfrom(1024)
                message = message.decode()
                # Se il peer_address è conosciuto stampiamo il nick del peer, altrimenti stampiamo l'ip e la porta
                # Il messaggio avrà prima il nick e poi il messaggio, separati da -s-, quindi facciamo lo split
                nickname = message.split('-s-')[0]
                message = message.split('-s-')[1]
                if nickname in self.neighbor_list.keys():
                    # Se il peer_address è conosciuto stampiamo il nick del peer
                    # Voglio che il messaggio lo stampi in una nuova riga, quindi uso \n
                    print(f" \033[1;34m\nMessaggio ricevuto da {nickname}: {message}\033[1;34m")
                else:
                    # Altrimenti lo registro tra i vicini
                    self.neighbor_list[nickname] = (peer_address[0], peer_address[1])
                    # Stampo questa informazione in verde
                    print(
                        f"\033[1;32m\nNuovo vicino registrato: {nickname} ({peer_address[0]},{peer_address[1]})\033[0m")
                    # E stampo il messaggio
                    print(f"\033[1;34mMessaggio ricevuto da {nickname}: {message}\033[0m")
            except ConnectionResetError:
                print("\nPeer non raggiungibile")
                continue

    # Serve adesso un metodo per gestire il caso in cui l'oracolo ci comunichi che dobbiamo diventare noi oracoli
    def become_oracle(self):
        # DA COMPLETARE
        pass

    def registration(self):
        # Con questo metodo prima di tutto si cerca di registrarsi al proprio oracolo, altrimenti si passa agli altri
        # due
        for port in self.oracle_ports:
            try:
                self.register_with_oracle(port)
                break
            except ConnectionResetError:
                continue
        # Se non si riesce a registrarsi a nessun oracolo si stampa un messaggio di errore
        else:
            print("\033[1;31mNessun oracolo disponibile, riprovare più tardi")
            # attendiamo un input dall'utente per riprovare o uscire
            while True:
                choice = input("Premere 1 per riprovare, 2 per uscire: \033[0m")
                if choice == '1':
                    self.registration()
                    break
                elif choice == '2':
                    exit()
                else:
                    print("Scelta non valida")
                    continue

    # Implementiamo un metodo che fa partire tutti i thread necessari
    def start_threads(self):
        self.SM.start()
        self.RM.start()
        self.RQ.start()


# Creiamo un peer per testare il funzionamento della classe
# Esempio di utilizzo della classe Peer
ip = 'localhost'  # Modifica con l'indirizzo IP del tuo peer
port = randint(1000, 5000)  # Modifica con la porta del tuo peer
# Creiamo un peer che si registra a un oracolo casuale
# Facciamo si che ogni Peer casualmente si registri a un oracolo qualsiasi tra i tre che abbiamo creato
# Quindi facciamo si che venga selezionata casualmente una porta tra le tre degli oracoli, che sono 9999 9996 e 9993
oracle_port = choice([9999, 9996, 9993])
nick = input("Inserisci il tuo nickname: ")
peer = Peer(nick, ip, port, oracle_port)
