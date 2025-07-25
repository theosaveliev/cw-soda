import re
from pathlib import Path
from typing import BinaryIO, TextIO

import click
from nacl.encoding import Encoder
from nacl.public import PrivateKey, PublicKey

from cw_soda.cryptography.kdf import align_salt, hash_salt
from cw_soda.encoders import RawEncoder, decode_bytes, encode_str

__all__ = [
    "read_str",
    "read_bytes",
    "read_groups",
    "read_message",
    "read_ciphretext",
    "remove_whitespace",
    "init_keypair",
    "get_salt",
    "print_stats",
    "write_output",
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


def init_keypair(private_key: TextIO, public_key: TextIO, in_enc: Encoder):
    priv = read_bytes(private_key)
    priv = PrivateKey(priv, in_enc)
    pub = read_bytes(public_key)
    pub = PublicKey(pub, in_enc)
    return priv, pub


def get_salt(file: TextIO, decode: bool, in_enc: Encoder) -> bytes:
    salt = read_bytes(file)
    if decode:
        raw = in_enc.decode(salt)
        return align_salt(raw)

    return hash_salt(salt)


def print_stats(plain, cipher):
    click.echo(f"Plaintext length: {len(plain)}", err=True)
    click.echo(f"Ciphertext length: {len(cipher)}", err=True)
    overhead = len(cipher) / len(plain)
    click.echo(f"Overhead: {overhead:.3f}", err=True)


def write_output(output_file: Path | None, data: bytes, out_enc: Encoder):
    if output_file is not None:
        if output_file.exists():
            click.confirm("Overwrite the output file?", default=False, abort=True)

        output_file.write_bytes(data)
    elif out_enc == RawEncoder:
        click.confirm("Print binary file to the terminal?", default=False, abort=True)
        click.echo(data)
    else:
        click.echo(decode_bytes(data))


def read_message(message_file: BinaryIO, in_enc: Encoder):
    data = message_file.read()
    if in_enc == RawEncoder:
        return data

    data = decode_bytes(data).strip()
    return encode_str(data)


def read_ciphretext(message_file: BinaryIO, in_enc: Encoder):
    data = message_file.read()
    if in_enc == RawEncoder:
        return data

    data = remove_whitespace(decode_bytes(data))
    return encode_str(data)
