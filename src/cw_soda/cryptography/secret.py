from nacl.encoding import Encoder
from nacl.pwhash import argon2id
from nacl.secret import SecretBox
from nacl.utils import EncryptedMessage, random

__all__ = ["encrypt", "decrypt", "generate_key", "kdf"]


def encrypt(key: bytes, data: bytes, encoder: Encoder) -> EncryptedMessage:
    box = SecretBox(key, encoder)
    return box.encrypt(data, encoder=encoder)


def decrypt(key: bytes, data: bytes, encoder: Encoder) -> bytes:
    box = SecretBox(key, encoder)
    return box.decrypt(data, encoder=encoder)


def generate_key() -> bytes:
    return random(SecretBox.KEY_SIZE)


def kdf(password: bytes, salt: bytes, encoder: Encoder) -> bytes:
    ops = argon2id.OPSLIMIT_INTERACTIVE
    mem = argon2id.MEMLIMIT_INTERACTIVE
    return argon2id.kdf(SecretBox.KEY_SIZE, password, salt, ops, mem, encoder)
