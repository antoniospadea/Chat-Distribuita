# Rete Peer-to-Peer con Oracoli

Questo repository contiene un'implementazione in Python di una rete peer-to-peer con oracoli. La rete consiste in diversi peer che comunicano tra loro tramite gli oracoli, che fungono da server di registrazione.

## Introduzione
Questo programma implementa una rete Peer-to-Peer (P2P) utilizzando Python. La rete consente ai peer di comunicare tra loro senza la necessità di un server centrale. Ogni peer agisce sia come client che come server, consentendo lo scambio di informazioni dirette tra di loro. Il programma include due classi principali: `Peer` e `Oracle`. La classe `Peer` rappresenta un peer nella rete e si occupa della comunicazione e dell'interazione con altri peer, mentre la classe `Oracle` funge da registro centralizzato per i peer registrati.


## Componenti

### Classe Oracle
- `Oracle_Lez_Cappa.py`: Questo file contiene l'implementazione della classe `Oracle`, che rappresenta il server dell'oracolo. L'oracolo ascolta le richieste di registrazione dai peer e mantiene una lista dei peer registrati.

La classe `Oracle` rappresenta l'oracolo nella rete P2P. Funge da registro centralizzato per i peer registrati e gestisce le richieste di registrazione e query. Di seguito sono elencati i metodi principali della classe:

 `__init__(self, nick, ip, port)`: Il metodo di inizializzazione dell'oracolo. Imposta l'indirizzo IP, la porta e il nickname dell'oracolo, oltre a creare il socket necessario.
- `peer_registration(self, message, address)`: Gestisce le richieste di registrazione da parte dei peer, aggiungendo o rimuovendo i peer registrati dalla lista e inviando conferme ai peer interessati.
- `peer_query(self, message, address)`: Gestisce le richieste di query da parte dei peer, restituendo le informazioni richieste sui peer registrati o un messaggio di non disponibilità.
- `receive_message(self)`: Riceve i messaggi inviati dai peer registrati e li instrada alle funzioni appropriate in base al tag del messaggio.
- `receive_query(self)`: Riceve le richieste di query dai peer e le gestisce, inviando le risposte corrispondenti.
- `receive_communication(self)`: Riceve i messaggi di comunicazione da altri oracoli e aggiorna la lista dei peer registrati in base ai messaggi ricevuti.
- `send_communication(self, tag, nick, address)`: Invia messaggi di comunicazione ad altri oracoli per aggiornare le loro liste dei peer registrati.
- `start_threads(self)`: Avvia i thread per gestire le diverse comunicazioni in modo asincrono.



### Classe Peer
- `Peer_Lez_Cappa.py`: Questo file contiene l'implementazione della classe `Peer`, che rappresenta un peer nella rete. Ogni peer viene assegnato un indirizzo IP e un numero di porta casuali e si registra presso gli oracoli per unirsi alla rete.

La classe `Peer` rappresenta un peer nella rete P2P. Gestisce la registrazione al network, l'invio e la ricezione di messaggi ai/vicini e la comunicazione con l'oracolo. Ecco una panoramica dei metodi principali della classe:

- `__init__(self, nick, ip, port)`: Il metodo di inizializzazione del peer. Viene utilizzato per impostare l'indirizzo IP, la porta e il nickname del peer, oltre a creare e collegare i socket necessari.
- `register_with_oracle(self)`: Registra il peer presso l'oracolo utilizzando il protocollo UDP. Invia un messaggio di registrazione contenente il nickname del peer all'oracolo.
- `send_message(self)`: Invia un messaggio a un altro peer nella rete. Il messaggio viene inviato tramite il socket `peer_socket`.
- `send_query(self, nick)`: Invia una query per ottenere informazioni su un peer specifico. La query può essere inviata sia a un vicino che all'oracolo.
- `receive_query(self)`: Riceve le query dai vicini o dall'oracolo. Gestisce le richieste inviate al peer e invia le risposte corrispondenti.
- `receive_message(self)`: Riceve i messaggi dai vicini. Stampa il messaggio ricevuto insieme all'indirizzo del mittente.
- `become_oracle(self)`: Gestisce il caso in cui l'oracolo richiede al peer di diventare un nuovo oracolo. Questa funzione non è ancora implementata.

- `main.py`: Questo file serve come punto di ingresso del programma. Inizializza tre istanze della classe `Oracle` e un'istanza della classe `Peer` per testare la funzionalità della rete.

## Requisiti

- Python 3.x

## Come Eseguire

Avviare l'oracolo:
- Aprire un terminale o prompt dei comandi.
- Navigare nella directory del programma.
- Eseguire il seguente comando:

python Oracle_Lez_Cappa.py


Avviare un peer:
- Aprire un nuovo terminale o prompt dei comandi.
- Navigare nella directory del programma.
- Eseguire il seguente comando:

python main.py

- Seguire le istruzioni per inserire un nickname per il peer.

Interazione con il Programma:
- Una volta avviato il peer, è possibile inviare messaggi ad altri peer nella rete.
- Il peer può anche registrarsi presso l'oracolo e inviare query ad altri peer o all'oracolo stesso.

Terminazione del Programma:
- Per terminare il programma, premere Invio nel terminale o prompt dei comandi in cui è in esecuzione il peer.
- L'oracolo può essere terminato premendo Ctrl+C nel suo terminale o prompt dei comandi.


## Personalizzazione

- Gli oracoli vengono inizializzati con le seguenti informazioni:
- Primo oracolo: Indirizzo IP - 'localhost', Porta - 9999, Nickname - 'primo_oracolo'
- Secondo oracolo: Indirizzo IP - 'localhost', Porta - 9998, Nickname - 'secondo_oracolo'
- Terzo oracolo: Indirizzo IP - 'localhost', Porta - 9997, Nickname - 'terzo_oracolo'
È possibile modificare questi dettagli nel file `main.py` in base alle proprie esigenze.

- Il peer viene assegnato un indirizzo IP e un numero di porta casuali nell'intervallo compreso tra 1000 e 5000. È possibile modificare questo intervallo nella classe `Peer` nel file `Peer_Lez_Cappa.py` se necessario.

## Contributi

Sono benvenuti contributi a questo progetto. Se si riscontrano problemi o si hanno suggerimenti per miglioramenti, è possibile aprire una segnalazione o inviare una richiesta di modifica.

## Licenza

Questo progetto è concesso in licenza sotto la Licenza MIT.
