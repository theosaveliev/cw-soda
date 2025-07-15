from nacl.encoding import Encoder, RawEncoder
from nacl.hash import blake2b
from nacl.public import PrivateKey
from nacl.pwhash import argon2id
from nacl.pwhash.argon2id import (
    MEMLIMIT_INTERACTIVE,
    MEMLIMIT_MODERATE,
    MEMLIMIT_SENSITIVE,
    OPSLIMIT_INTERACTIVE,
    OPSLIMIT_MODERATE,
    OPSLIMIT_SENSITIVE,
    SALTBYTES,
)

__all__ = ["kdf", "kdf_profiles", "hash_salt", "align_salt"]

kdf_profiles = {
    "interactive": (OPSLIMIT_INTERACTIVE, MEMLIMIT_INTERACTIVE),
    "moderate": (OPSLIMIT_MODERATE, MEMLIMIT_MODERATE),
    "sensitive": (OPSLIMIT_SENSITIVE, MEMLIMIT_SENSITIVE),
}


def kdf(password: bytes, salt: bytes, profile, out_enc: Encoder) -> bytes:
    return argon2id.kdf(PrivateKey.SIZE, password, salt, *profile, encoder=out_enc)


def hash_salt(salt: bytes) -> bytes:
    return blake2b(salt, digest_size=SALTBYTES, encoder=RawEncoder)


def align_salt(salt: bytes) -> bytes:
    if len(salt) >= SALTBYTES:
        return salt[:SALTBYTES]

    padding = bytes(SALTBYTES - len(salt))
    return padding + salt
