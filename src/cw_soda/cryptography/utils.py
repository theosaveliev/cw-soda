from nacl.pwhash import argon2id
from nacl.utils import random

__all__ = ["generate_salt", "align_salt"]

slen = argon2id.SALTBYTES


def generate_salt() -> bytes:
    return random(slen)


def align_salt(salt: bytes) -> bytes:
    if len(salt) < slen:
        raise ValueError(f"The salt must be {slen} bytes")

    return salt[0:slen]
