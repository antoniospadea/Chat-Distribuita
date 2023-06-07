from realignment import *
from registration import *
from communication import receive_registrations, receive_disconnections
from query import *
from interface import *


class Oracle:
    def __init__(self, nick, ip, port):
        self.peer_list = {}
        if ip == 'localhost':
            self.ip = '127.0.0.1'
        self.port = port
        self.nickname = nick

        self.communication_socket = socket_setup(self.ip, self.port - 1)
        self.registr_socket = socket_setup(self.ip, self.port)
        self.query_socket = socket_setup(self.ip, self.port - 2)

        self.oracle_setup()

    def receive_query(self):
        while True:
            try:
                message, address = self.query_socket.recvfrom(1024)
            except ConnectionResetError:
                continue
            message = message.decode()
            if message.startswith('-q'):
                peer_query(self.query_socket, self.peer_list, message, address)
            elif message.startswith('-k'):
                give_key(self.query_socket, self.peer_list, message, address)
            else:
                pass

    def receive_from_oracle(self):
        while True:
            try:
                message, address = self.communication_socket.recvfrom(65536)
                message = message.decode()
                if message.startswith('-r'):
                    receive_registrations(self, message)
                elif message.startswith('-d'):
                    receive_disconnections(self, message)
                elif message.startswith('-l0'):
                    receive_realignment_request(self, address)
                elif message.startswith('-l1'):
                    realign(self, message)
            except ConnectionResetError:
                pass

    def receive_registration(self):
        while True:
            message, address = self.registr_socket.recvfrom(1024)
            message = message.decode()
            if message.startswith('-r'):
                peer_registration(self, message, address)
            elif message.startswith('-d'):
                peer_disconnection(self, message, address)
            else:
                pass

    def oracle_setup(self):
        interface_Oracolo(self.ip, self.port)
        thread_setup(self.receive_query)
        thread_setup(self.receive_from_oracle)
        thread_setup(self.receive_registration)
        realignment_ask(self)


# Creiamo un Oracolo per testare il funzionamento della classe
if __name__ == '__main__':
    ip = 'localhost'
    port = 9993
    nick = 'Oracle3'
    oracle = Oracle(nick, ip, port)
