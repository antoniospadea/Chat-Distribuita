import rsa


def keys():
    """
    La funzione genera le chiavi pubbliche e private che servono per la 
    crittografia

    Returns
    -------
    public_key_pem : chiave pubblica
    private_key : chiave privata

    """
    public_key, private_key = rsa.newkeys(1024)
    public_key_pem = public_key.save_pkcs1().decode()
    return public_key_pem, private_key


def crypt(message, key):
    """
    La funzione cripta il messagio con la chiave

    Parameters
    ----------
    message : stringa da criptare
    key : chaive

    Returns
    -------
    message : stringa criptata

    """
    key = rsa.PublicKey.load_pkcs1(key)
    message = message.encode('utf-8')
    message = rsa.encrypt(message, key)
    return message


def decrypt(message, key):
    """
    La funzione decripta il messagio con la chiave

    Parameters
    ----------
    message : stringa da decriptare
    key : chaive

    Returns
    -------
    message : stringa decriptata

    """
    message = rsa.decrypt(message, key)
    message = message.decode()
    return message
