from nacl.encoding import Encoder
from nacl.public import Box, PrivateKey, PublicKey

__all__ = ["encrypt", "decrypt"]


def encrypt(private: PrivateKey, public: PublicKey, data: bytes, out_enc: Encoder):
    box = Box(private, public)
    return box.encrypt(data, encoder=out_enc)


def decrypt(private: PrivateKey, public: PublicKey, data: bytes, in_enc: Encoder):
    box = Box(private, public)
    return box.decrypt(data, encoder=in_enc)
