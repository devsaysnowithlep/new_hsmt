import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from xfiles.models import *

class AESCipher(object):
    '''Implement AES cipher for unicode key and plaintext'''

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = raw.encode('utf-8')
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode('utf-8')

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def encode(raw, key):
    if raw == '':
        return raw
    encoder = AESCipher(key)
    return encoder.encrypt(raw).decode('utf-8')

def decode(cipher, key):
    if cipher == '':
        return cipher
    decoder = AESCipher(key)
    return decoder.decrypt(cipher)