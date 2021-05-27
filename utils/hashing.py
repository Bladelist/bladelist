import hashlib
import binascii

from django.contrib.auth import settings


class Hasher(object):
    def __init__(self, method="sha256",
                 salt=settings.ENCRYPTION_SALT,
                 iterations=int(settings.ENCRYPTION_ITERATION)):
        self.method = method
        self.salt = bytes(salt, 'utf-8')
        self.iterations = iterations

    def get_hashed_pass(self, text):
        hash_obj = hashlib.pbkdf2_hmac(self.method,
                                       bytes(text, 'utf-8'), self.salt, self.iterations)
        return str(binascii.hexlify(hash_obj))
