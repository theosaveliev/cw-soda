import re
from typing import TextIO

import click
from nacl.encoding import Encoder
from nacl.public import PrivateKey, PublicKey

from cw_soda.cryptography.utils import align_salt, generate_salt, hash_salt
from cw_soda.encoders import decode_bytes, encode_str

__all__ = [
    "read_str",
    "read_bytes",
    "read_groups",
    "remove_whitespace",
    "init_keypair",
    "get_salt",
    "print_stats",
    "print_salt",
]


def read_str(buff: TextIO) -> str:
    return buff.read().strip()


def read_bytes(buff: TextIO) -> bytes:
    return encode_str(read_str(buff))


def remove_whitespace(data: str) -> str:
    return re.sub(r"\s", "", data)


# CW is sent in 5-letter groups
def break_into_groups(data: str) -> list:
    return [data[i : i + 5] for i in range(0, len(data), 5)]


def read_groups(buff: TextIO) -> list:
    """Reads the input as 5-letter groups."""
    text = read_str(buff)
    text = remove_whitespace(text)
    return break_into_groups(text)


def init_keypair(private_key: TextIO, public_key: TextIO, encoder: Encoder):
    priv = read_bytes(private_key)
    priv = PrivateKey(priv, encoder)
    pub = read_bytes(public_key)
    pub = PublicKey(pub, encoder)
    return priv, pub


def get_salt(file: TextIO | None, decode: bool, encoder: Encoder) -> bytes:
    if file is None:
        return generate_salt()

    salt = read_bytes(file)
    if decode:
        raw = encoder.decode(salt)
        return align_salt(raw)

    return hash_salt(salt)


def print_stats(plain: str, cipher: str):
    click.echo(f"Plaintext length: {len(plain)}", err=True)
    click.echo(f"Ciphertext length: {len(cipher)}", err=True)
    overhead = len(cipher) / len(plain)
    click.echo(f"Overhead: {overhead:.3f}", err=True)


def print_salt(salt: bytes, encoder: Encoder):
    out = encoder.encode(salt)
    click.echo(f"Salt: {decode_bytes(out)}", err=True)
