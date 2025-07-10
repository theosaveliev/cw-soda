from nacl.encoding import Encoder
from nacl.secret import SecretBox
from nacl.utils import EncryptedMessage

__all__ = ["encrypt", "decrypt"]


def encrypt(key: bytes, data: bytes, encoder: Encoder) -> EncryptedMessage:
    box = SecretBox(key, encoder)
    return box.encrypt(data, encoder=encoder)


def decrypt(key: bytes, data: bytes, encoder: Encoder) -> bytes:
    box = SecretBox(key, encoder)
    return box.decrypt(data, encoder=encoder)
