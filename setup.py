import socket
from threading import Thread


def socket_setup(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    return s


def thread_setup(method):
    t = Thread(target=method)
    t.start()


def print_list(list: dict):
    output = ', '.join(
        [f"{key}: ({', '.join(map(str, values[:2]))})" for key, values in list.items()])
    print(f"Lista dei Peer registrati: {output}")
