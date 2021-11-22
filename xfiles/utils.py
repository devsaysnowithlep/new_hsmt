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
    if not raw:
        return raw
    encoder = AESCipher(key)
    return encoder.encrypt(raw).decode('utf-8')

def decode(cipher, key):
    if not cipher:
        return cipher
    decoder = AESCipher(key)
    return decoder.decrypt(cipher)

def change_pwd_for_xfile(xfile, old_key, new_key):
    for content in xfile.contents.all():
        for detail in content.details.all():
            detail.text = encode(decode(detail.text, old_key), new_key)
            detail.save()

    for attack_log in xfile.attack_logs:
        attack_log.process = encode(decode(attack_log.process, old_key), new_key)
        attack_log.result = encode(decode(attack_log.result, old_key), new_key)
        attack_log.save()

    for xfile_log in xfile.xfile_logs:
        xfile_log.contents = encode(decode(xfile_log.contents, old_key), new_key)
        xfile_log.attack_logs = encode(decode(xfile_log.attack_logs, old_key), new_key)
        xfile_log.save()

def change_pwd_for_xfile_department(department_id, old_key, new_key):
    xfiles = set(XFile.objects.filter(department__id=department_id))
    for xfile in xfiles:
        change_pwd_for_xfile(xfile, old_key, new_key)
