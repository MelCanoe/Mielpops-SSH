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

with open(dataFolder + '/filesystem.json', 'r') as fsFile:
    fs = load(fsFile)


# ===== Classes =====

class ShellHandler:
    def __init__(self, channel: Channel):
        self.channel = channel
        self.buffer = ""
        self.pwd = "/home/user1"

    def get_folder_from_path(self, path: str):
        if path == "/":
            return fs['/']
        try:
            splittedPath = path.split('/')
            folderContent = fs['/']
            for x in splittedPath[1:]:
                folderContent = folderContent[x]
            return folderContent
        except KeyError:
            return False

    def handle_command(self, command: list[str]):
        self.channel.send("\r\n")
        if command[0] == 'ls':
            if len(command) == 1:
                path = self.pwd
            elif command[1].startswith('/'):
                path = command[1]
            else:
                path = self.pwd.rstrip('/') + '/' + command[1]

            content = self.get_folder_from_path(path)
            if content is False:
                self.channel.send(f"ls: cannot access '{command[1]}': No such file or directory\r\n")
            elif content is None:
                self.channel.send(f"{command[1]}\r\n")
            else:
                for item in content:
                    self.channel.send(f'{item} ')
                self.channel.send("\r\n")
        elif command[0] == 'cd':
            if len(command) == 1:
                self.pwd = "/home/user1"
            else:
                path = command[1]
                if path == '..':
                    self.pwd = '/'.join(self.pwd.split('/')[:-1]) or '/'
                elif path.startswith('/'):
                    if self.get_folder_from_path(path) is not False:
                        self.pwd = path
                else:
                    fullPath = self.pwd.rstrip('/') + '/' + path
                    if self.get_folder_from_path(fullPath) is not False:
                        self.pwd = fullPath
        elif command[0] == 'whoami':
            self.channel.send("user1\r\n")
        elif command[0] == 'pwd':
            self.channel.send(self.pwd + '\r\n')
        else:
            self.channel.send(
                f"bash: {''.join(command)}: command not found\r\n"
            )

    def input_loop(self):
        self.channel.send("$ ") 
        while True:
            data = self.channel.recv(1024)
            if not data:
                break

            for c in data.decode():
                if c == '\r':
                    self.handle_command(self.buffer.split(' '))
                    self.buffer = ''
                    self.channel.send("$ ")
                elif c == '\x7f':
                    if len(self.buffer) > 0:
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
