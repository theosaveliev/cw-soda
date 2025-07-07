from nacl.encoding import Encoder
from nacl.public import Box, PrivateKey, PublicKey
from nacl.pwhash import argon2id
from nacl.utils import EncryptedMessage

__all__ = ["encrypt", "decrypt", "kdf"]


def encrypt(
    private: PrivateKey, public: PublicKey, data: bytes, encoder: Encoder
) -> EncryptedMessage:
    box = Box(private, public)
    return box.encrypt(data, encoder=encoder)


def decrypt(
    private: PrivateKey, public: PublicKey, data: bytes, encoder: Encoder
) -> bytes:
    box = Box(private, public)
    return box.decrypt(data, encoder=encoder)


def kdf(password: bytes, salt: bytes, encoder: Encoder) -> bytes:
    ops = argon2id.OPSLIMIT_INTERACTIVE
    mem = argon2id.MEMLIMIT_INTERACTIVE
    return argon2id.kdf(PrivateKey.SIZE, password, salt, ops, mem, encoder)
