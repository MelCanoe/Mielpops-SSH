# ===== Imports =====

from os.path import dirname, abspath, isfile
from paramiko import RSAKey, Transport, ServerInterface
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


class MielpopsServer(ServerInterface):
    def check_auth_password(self, user, password):
        print(f'Tentative : {user}:{password}')
        if user in accounts.keys() and password == accounts[user]:
            return AUTH_SUCCESSFUL
        return AUTH_FAILED

    def check_channel_request(self, kind, channelId):
        if kind == 'session':
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


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
    if channel is not None:
        print('Channel ouvert')


# ===== Execution =====

if __name__ == '__main__':
    main()
