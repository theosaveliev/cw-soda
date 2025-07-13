from nacl.encoding import Encoder
from nacl.public import Box, PrivateKey, PublicKey
from nacl.pwhash import argon2id

__all__ = ["encrypt", "decrypt", "kdf"]


def encrypt(private: PrivateKey, public: PublicKey, data: bytes, out_enc: Encoder):
    box = Box(private, public)
    return box.encrypt(data, encoder=out_enc)


def decrypt(private: PrivateKey, public: PublicKey, data: bytes, in_enc: Encoder):
    box = Box(private, public)
    return box.decrypt(data, encoder=in_enc)


def kdf(password: bytes, salt: bytes, out_enc: Encoder) -> bytes:
    ops = argon2id.OPSLIMIT_INTERACTIVE
    mem = argon2id.MEMLIMIT_INTERACTIVE
    return argon2id.kdf(PrivateKey.SIZE, password, salt, ops, mem, out_enc)
