import re
from typing import TextIO

import click
from nacl.encoding import Encoder
from nacl.public import PrivateKey, PublicKey

from cw_soda.encoders import encode_str

__all__ = [
    "read_str",
    "read_bytes",
    "read_groups",
    "print_stats",
    "remove_whitespace",
    "init_keypair",
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
    """Reads the input as 5-letter groups for CW."""
    text = read_str(buff)
    text = remove_whitespace(text)
    return break_into_groups(text)


def init_keypair(private_key: TextIO, public_key: TextIO, encoder: Encoder):
    priv = read_bytes(private_key)
    priv = PrivateKey(priv, encoder)
    pub = read_bytes(public_key)
    pub = PublicKey(pub, encoder)
    return priv, pub


def print_stats(plain: str, cipher: str):
    click.echo(f"Plaintext length: {len(plain)}", err=True)
    click.echo(f"Ciphertext length: {len(cipher)}", err=True)
    redun = len(cipher) / len(plain)
    click.echo(f"Redundancy: {redun:.3f}", err=True)
