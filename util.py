from Crypto.Cipher import AES
from os import remove


def decryptTS(name):
    buffer = open(name, 'rb').read()
    key = open(name.replace('.ts', '.key'), 'rb').read()
    cryptor = AES.new(key, AES.MODE_CBC, bytes(16))
    with open(name, 'wb') as f:
        f.write(cryptor.decrypt(buffer))
    remove(name.replace('.ts', '.key'))


if __name__ == "__main__":
    from sys import argv
    for ii in argv[1:]:
        if ii.endswith('.key'):
            continue
        decryptTS(ii)
