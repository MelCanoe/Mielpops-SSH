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
