# Rete Peer-to-Peer con Oracoli

Questo repository contiene un'implementazione in Python di una rete peer-to-peer con oracoli. La rete consiste in diversi peer che comunicano tra loro tramite gli oracoli, che fungono da server di registrazione.

## Componenti

- `Oracle_Lez_Cappa.py`: Questo file contiene l'implementazione della classe `Oracle`, che rappresenta il server dell'oracolo. L'oracolo ascolta le richieste di registrazione dai peer e mantiene una lista dei peer registrati.
- `Peer_Lez_Cappa.py`: Questo file contiene l'implementazione della classe `Peer`, che rappresenta un peer nella rete. Ogni peer viene assegnato un indirizzo IP e un numero di porta casuali e si registra presso gli oracoli per unirsi alla rete.
- `main.py`: Questo file serve come punto di ingresso del programma. Inizializza tre istanze della classe `Oracle` e un'istanza della classe `Peer` per testare la funzionalità della rete.

## Requisiti

- Python 3.x

## Come Eseguire

1. Clonare questo repository sulla propria macchina locale.
2. Aprire un terminale e navigare nella cartella del progetto.
3. Eseguire il seguente comando per avviare il programma:
4. Seguire le istruzioni a schermo per fornire le informazioni richieste, come il nickname per il peer.
5. Il programma inizializzerà gli oracoli e il peer, e il peer cercherà di registrarsi presso gli oracoli.
6. Una volta che la registrazione avrà successo, il peer farà parte della rete peer-to-peer e potrà comunicare con altri peer tramite gli oracoli.

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
