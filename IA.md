## Claude 14/11 :

Demande : Génère moi une arborescence crédible

Gardé :
``` json
{
    "/": {
        "bin": {},
        "etc": {
            "passwd": null,
            "hostname": null,
            "shadow": null
        },
        "home": {
            "admin": {
                ".bashrc": null,
                ".ssh": {
                    "authorized_keys": null
                },
                "Documents": {},
                "Downloads": {}
            }
        },
        "root": {
            ".bashrc": null
        },
        "tmp": {},
        "var": {
            "log": {
                "syslog": null
            }
        }
    }
}
```

## Claude 14/11 :

Demande : Aide moi sur le tout début, c'est quoi les fonctions / méthodes qu'il faut pour faire le serveur.

Gardé :

``` python
transport = paramiko.Transport(client_socket)
host_key = paramiko.RSAKey.generate(2048)
transport.add_server_key(host_key)
server = TonServerInterface()
transport.start_server(server=server)
channel = transport.accept(30)
```

## Claude 14/11 :

Demande : Tu peux m'aider avec la structure de la classe de mon serveur. J'aimerai voir à quoi ça ressemble.

Gardé :

``` python
from paramiko import ServerInterface, AUTH_SUCCESSFUL, OPEN_SUCCEEDED

class HoneypotServer(ServerInterface):

    def check_auth_password(self, username, password):
        # Appelée quand le client essaie un user/pass
        # Tu return AUTH_SUCCESSFUL ou AUTH_FAILED
        return AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        # Appelée quand le client veut ouvrir un canal
        if kind == "session":
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        # Appelée quand le client demande un shell
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        # Appelée quand le client demande un pseudo-terminal
        return True
```

## Claude 16/11 :

Demande : Aide moi à faire le README.md

Gardé :

# MielpopsSSH
 
A lightweight SSH honeypot built in Python using Paramiko.
 
## What is it?
 
MielpopsSSH is a fake SSH server that simulates a Linux environment to attract and monitor attackers. It logs every connection attempt, authentication try, and command entered by intruders.
 
The server speaks real SSH protocol (key exchange, encryption, authentication), but everything behind it is fake.
 
## Features

- **Fake interactive shell** — Simulates bash with command echo, backspace handling, and prompt
- **Virtual filesystem** — JSON-based fake directory structure with `ls`, `cd`, `pwd` navigation
- **Authentication logging** — Records every username/password combination attempted
- **Command logging** — Tracks every command entered by authenticated attackers
- **Multi-threaded** — Handles multiple simultaneous connections
- **Configurable accounts** — Define which credentials grant access via a JSON file

## Project structure
 
```
MielpopsSSH/
├── src/
│   └── main.py
├── data/
│   ├── accounts.json     # Allowed credentials
│   ├── filesystem.json   # Virtual filesystem structure
│   └── history.json      # Attack logs (auto-generated)
├── .gitignore
└── README.md
```
 
## Setup
 
### Requirements
 
- Python 3.10+
- Paramiko

### Installation
 
```bash
git clone <repo-url>
cd MielpopsSSH
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install paramiko
```
 
### Configuration
 
**Accounts** : Edit `data/accounts.json` to define which credentials are accepted:
 
```json
{
    "admin": "admin",
    "root": "root"
}
```
 
**Filesystem** : Edit `data/filesystem.json` to define the fake directory tree. Directories are JSON objects `{}`, files are `null`:
 
```json
{
    "/": {
        "home": {
            "user1": {
                "Documents": {},
                ".bashrc": null
            }
        },
        "etc": {
            "passwd": null
        }
    }
}
```
 
## Usage
 
```bash
python src/main.py
```
 
The honeypot listens on port 2222 by default. To test it:
 
```bash
ssh admin@127.0.0.1 -p 2222
```

## Supported commands
 
| Command | Behavior |
|---------|----------|
| `ls [path]` | Lists virtual directory contents |
| `cd [path]` | Navigates the virtual filesystem |
| `pwd` | Prints current working directory |
| `whoami` | Returns the logged-in username |
 
Any other command returns `bash: <command>: command not found`.
 
## Logs
 
Attack logs are stored in `data/history.json` and organized by IP address:
 
```json
{
    "192.168.1.42": {
        "commands": {
            "1700000000": "ls -la",
            "1700000005": "cat /etc/passwd"
        },
        "auth": {
            "1700000000": {
                "user": "root",
                "pass": "123456",
                "status": "failed"
            }
        }
    }
}
```

Rejeté :

## How it works
 
1. A TCP socket listens for incoming connections
2. Paramiko wraps each connection with the SSH protocol (key exchange, encryption)
3. The `MielpopsServer` class handles authentication and logs every attempt
4. On successful auth, a `ShellHandler` provides a fake interactive bash shell
5. All commands and auth attempts are logged to `data/history.json` with timestamps and source IPs

## Disclaimer
 
This tool is intended for **educational purposes only** as part of a cybersecurity school project. Only deploy honeypots on networks you own or have explicit permission to monitor.

## Claude 16/11

Demande : Comment faire un signal pour les interruptions claviers (ctrl + d) dans le main.py.

Gardé :
``` python
    try:
        while True:
            clientSocket, clientAddr = serverSocket.accept()
            newThread = threading.Thread(
                target=handle_client,
                args=(clientSocket, clientAddr, serverLogs),
                daemon=True
            )
            newThread.start()
    except KeyboardInterrupt:
        print("\n[!] Arrêt du serveur.")
    finally:
        serverSocket.close()
```

``` python
elif c == '\x04':
    self.channel.close()
    return
```

## Claude 16//11

Demande : L'interruption ne fonctionne pas

Gardé : Applique un timeout sur les socket accept avec "serverSocket.settimeout(1)" pour couper l'attente et savoir si une interruption est demandée.