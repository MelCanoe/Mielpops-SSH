# ===== Imports =====

from os.path import dirname, abspath, isfile
from paramiko import RSAKey, Transport, ServerInterface, Channel
from paramiko.common import (
    AUTH_SUCCESSFUL,
    AUTH_FAILED,
    OPEN_SUCCEEDED,
    OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
)
from json import load
import socket


# ===== Variables =====

srcFolder = dirname(abspath(__file__))
dataFolder = srcFolder + '/../data'

with open(dataFolder + '/accounts.json', 'r') as accountsFile:
    accounts = load(accountsFile)
    print(accounts)


# ===== Classes =====

class ShellHandler:
    def __init__(self, channel: Channel):
        self.channel = channel
        self.buffer = ""

    def input_loop(self):
        self.channel.send("$ ")
        while True:
            data = self.channel.recv(1024)
            if not data:
                break

            for c in data.decode():
                if c == '\r':
                    print(f'Commande complete : {self.buffer}')
                    self.buffer = ''
                elif c == '\x7f':
                    self.buffer = self.buffer[0:-1]
                    self.channel.send('\b \b')
                else:
                    self.buffer += c
                    self.channel.send(c)


class MielpopsServer(ServerInterface):
    def check_auth_password(self, user, password):
        print(f'Tentative : {user}:{password}')
        if user in accounts.keys() and password == accounts[user]:
            return AUTH_SUCCESSFUL
        return AUTH_FAILED

    def check_channel_request(self, kind, channel):
        if kind == 'session':
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True


# ===== Functions =====


def get_key() -> RSAKey:
    if not isfile(dataFolder + '/key'):
        newKey = RSAKey.generate(2048)
        newKey.write_private_key_file(dataFolder + '/key')
        return newKey
    currentKey = RSAKey(filename=dataFolder + '/key')
    return currentKey


def main() -> None:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('127.0.0.1', 2222))
    serverSocket.listen()

    clientSocket, clientAddr = serverSocket.accept()

    serverKey = get_key()

    transport = Transport(clientSocket)
    transport.add_server_key(serverKey)

    server = MielpopsServer()
    transport.start_server(server=server)
    channel = transport.accept(30)
    if channel is None:
        return

    shell = ShellHandler(channel)
    shell.input_loop()


# ===== Execution =====

if __name__ == '__main__':
    main()
