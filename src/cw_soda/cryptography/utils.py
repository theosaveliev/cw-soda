from nacl.encoding import RawEncoder
from nacl.hash import blake2b
from nacl.pwhash import argon2id
from nacl.utils import random

__all__ = ["generate_salt", "align_salt", "hash_salt"]

slen = argon2id.SALTBYTES


def generate_salt() -> bytes:
    return random(slen)


def align_salt(salt: bytes) -> bytes:
    if len(salt) >= slen:
        return salt[:slen]

    padding = bytes(slen - len(salt))
    return padding + salt


def hash_salt(salt: bytes) -> bytes:
    return blake2b(salt, digest_size=slen, encoder=RawEncoder)
