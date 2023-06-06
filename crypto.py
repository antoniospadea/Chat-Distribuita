import rsa


def keys():
    public_key, private_key = rsa.newkeys(1024)
    public_key_pem = public_key.save_pkcs1().decode()
    return public_key_pem, private_key


def crypt(message, key):
    key = rsa.PublicKey.load_pkcs1(key)
    message = message.encode('utf-8')
    message = rsa.encrypt(message, key)
    return message


def decrypt(message, key):
    message = rsa.decrypt(message, key)
    message = message.decode()
    return message
