COLORS = {"green": "\33[92m",
          "red": "\33[91m",
          "yellow": "\33[93m",
          "endc": "\33[0m",
          "blue": "\33[94m"}

blank = "                                                                             "


def print_banner():
    """Prints the slyther entry banner."""
    print_green("/////////////////////////////////////////////////////////////////////")
    print_green("///////////////////////// C H A T A.D.A. /////////////////////////////")
    print_green("/////////////////////////////////////////////////////////////////////")
    print("\n")


def print_green(msg):
    """Prints msg in green text."""
    print("{0}{1}{2}".format(COLORS["green"], msg, COLORS["endc"]))


def print_yellow(msg):
    """Prints msg in yellow text."""
    print("{0}{1}{2}".format(COLORS["yellow"], msg, COLORS["endc"]))


def print_red(msg):
    """Prints msg in red text."""
    print("{0}{1}{2}".format(COLORS["red"], msg, COLORS["endc"]))


def print_bar(msg):
    print("-" * (33 - int(.5 * len(msg))), msg, "-" * (33 - int(.5 * len(msg))))


def print_info_Oracolo():
    messaggio = "Ora puoi avviare un peer,il peer si potrà registrare all'oracolo mentre\n" \
                "l'oracolo rimarrà in attesa. Quando verrà effettuata una registrazione\n" \
                "nell'oracolo, verranno restituiti i dati del peer che si è registrato.\n "
    print_yellow(messaggio)


def print_info_Peer():
    messaggio = "Ora verrà avviato il peer, inserisci il nickname del peer che servirà\n" \
                "ad identificarlo durante le comunicazioni."
    print_yellow(messaggio)
    print("\n")


def print_info_chat():
    messaggio = "Ora verrà avviata la chat, inserisci il nickname del peer con cui \n" \
                "vuoi comunicare"
    print_yellow(messaggio)
    print_red("Per stampare la lista dei vicini disponibili premere -l")
    print_red("Per uscire Premere -d")


def avvio_registrazione_print():
    print_bar("Avvio Registrazione")


def avvio_chat():
    print_bar("Avvio Chat")
    print_info_chat()


def print_info_stato_Peer(response):
    if response.startswith('-r'):
        print_green("Registrazione completata con successo")
    elif response == '-pr':
        print_yellow("Registrazione completata con successo, nessun vicino disponibile")
    elif response.startswith('-n'):
        print_yellow("Registrazione non riuscita, nickname già registrato")
        nick = insert_Nickname()
        return nick


def interface_Oracolo(ip, port):
    print_banner()
    print_bar("Avvio Oracolo")
    print_green(f"Oracolo inizializzato: IP={ip}, Porta={port}")
    print("\n")
    print_info_Oracolo()
    print_bar("Peer registrati")


def insert_Nickname():
    print_green("Inserisci il tuo nickname: (solo lettere e numeri)")
    print_red("Per uscire Premere -d")
    nick = input()
    if nick == '-d':
        exit()
    while not nick.isalnum():
        nick = input("\33[91mNickname non valido, riprova: (solo lettere e numeri)\n \33[0m")
        if nick == '-d':
            exit()
    nick = nick.upper()
    return nick


def interface_Peer():
    print_banner()
    print_bar("Avvio Peer")
    print_info_Peer()
    print_bar("Inserimento Nickname")
    nick = insert_Nickname()
    print("\n")
    return nick


def print_risposta(msg):
    larghezza_totale = 110
    msg = "{0}{1}{2}".format(COLORS["blue"], msg, COLORS["endc"])
    frase = msg.rjust(larghezza_totale)
    print(frase)
