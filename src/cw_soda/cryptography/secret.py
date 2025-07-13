from nacl.encoding import Encoder
from nacl.secret import SecretBox

__all__ = ["encrypt", "decrypt"]


def encrypt(key: bytes, data: bytes, key_enc: Encoder, out_enc: Encoder):
    box = SecretBox(key, key_enc)
    return box.encrypt(data, encoder=out_enc)


def decrypt(key: bytes, data: bytes, key_enc: Encoder, in_enc: Encoder) -> bytes:
    box = SecretBox(key, key_enc)
    return box.decrypt(data, encoder=in_enc)
