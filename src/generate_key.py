# ===== Imports =====

from paramiko import RSAKey
from os.path import isfile, abspath, dirname


# ===== Variables =====

srcFolder = dirname(abspath(__file__))
dataFolder = srcFolder + '/../data'


# ===== Functions =====

def verify_key() -> None:
    if not isfile(dataFolder + '/key'):
        newKey = RSAKey.generate(2048)
        newKey.write_private_key_file(dataFolder + '/key')


# ===== Execution =====

if __name__ == '__main__':
    print(dataFolder)
