import string

from nacl.encoding import Encoder

from .functions import base_to_bytes, bytes_to_base, decode_bytes, encode_str

__all__ = ["Base26Encoder", "ALPHABET"]

ALPHABET = string.ascii_uppercase


class Base26Encoder(Encoder):
    @staticmethod
    def encode(data: bytes) -> bytes:
        return encode_str(bytes_to_base(data, ALPHABET))

    @staticmethod
    def decode(data: bytes) -> bytes:
        return base_to_bytes(decode_bytes(data), ALPHABET)
