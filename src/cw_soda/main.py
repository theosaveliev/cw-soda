from typing import TextIO

import click
from nacl.public import PrivateKey

from cw_soda.archivers import archivers, unarchivers
from cw_soda.cryptography.public import decrypt, encrypt, kdf
from cw_soda.cryptography.utils import align_salt, generate_salt
from cw_soda.encoders import decode_bytes, encode_key, encode_str, encoders
from cw_soda.error_search import checksum_calculators, error_search
from cw_soda.format_table import format_table
from cw_soda.io_utils import (
    init_keypair,
    print_stats,
    read_bytes,
    read_groups,
    read_str,
    remove_whitespace,
)
from cw_soda.soda_options import soda_options

file_arg = click.File(mode="r", encoding="utf-8", errors="strict")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="cw-soda")
def cli():
    pass


@click.command(help="Generate Private Key")
@soda_options.encoding
def genkey_cmd(encoding: str):
    enc = encoders[encoding]
    key = encode_key(PrivateKey.generate(), enc)
    click.echo(key)


@click.command(help="Get Public Key")
@click.argument("private_key_file", type=file_arg)
@soda_options.encoding
def pubkey_cmd(private_key_file: TextIO, encoding: str):
    enc = encoders[encoding]
    pk = read_bytes(private_key_file)
    pk = PrivateKey(pk, enc)
    pub = encode_key(pk.public_key, enc)
    click.echo(pub)


@click.command(help="Read key")
@click.argument("key_file", type=file_arg)
@soda_options.in_encoding
@soda_options.out_encoding
def readkey_cmd(key_file: TextIO, in_encoding: str, out_encoding: str):
    in_enc = encoders[in_encoding]
    out_enc = encoders[out_encoding]
    pk = read_bytes(key_file)
    pk = PrivateKey(pk, in_enc)
    pk = encode_key(pk, out_enc)
    click.echo(pk)


@click.command(help="Derive key")
@click.argument("password_file", type=file_arg)
@click.argument("salt_file", type=file_arg, required=False)
@soda_options.encoding
def kdf_cmd(password_file: TextIO, salt_file: TextIO, encoding: str):
    enc = encoders[encoding]
    password = read_bytes(password_file)
    if salt_file is not None:
        salt = read_bytes(salt_file)
        salt = enc.decode(salt)
        salt = align_salt(salt)
    else:
        salt = generate_salt()
        salt_out = enc.encode(salt)
        salt_out = decode_bytes(salt_out)
        click.echo(f"Salt: {salt_out}", err=True)

    key = kdf(password, salt, enc)
    key = decode_bytes(key)
    click.echo(key)


@click.command(help="Encrypt message")
@click.argument("private_key_file", type=file_arg)
@click.argument("public_key_file", type=file_arg)
@click.argument("message_file", type=file_arg)
@soda_options.encoding
@soda_options.compression
def encrypt_cmd(
    private_key_file: TextIO,
    public_key_file: TextIO,
    message_file: TextIO,
    encoding: str,
    compression: str,
):
    enc = encoders[encoding]
    priv, pub = init_keypair(private_key_file, public_key_file, enc)
    compress = archivers[compression]
    data_orig = read_str(message_file)
    data = encode_str(data_orig)
    data = compress(data)
    encrypted = encrypt(priv, pub, data, enc)
    encrypted = decode_bytes(encrypted)
    click.echo(encrypted)
    print_stats(data_orig, encrypted)


@click.command(help="Decrypt message")
@click.argument("private_key_file", type=file_arg)
@click.argument("public_key_file", type=file_arg)
@click.argument("message_file", type=file_arg)
@soda_options.encoding
@soda_options.compression
def decrypt_cmd(
    private_key_file: TextIO,
    public_key_file: TextIO,
    message_file: TextIO,
    encoding: str,
    compression: str,
):
    enc = encoders[encoding]
    priv, pub = init_keypair(private_key_file, public_key_file, enc)
    decompress = unarchivers[compression]
    data = read_str(message_file)
    data_orig = remove_whitespace(data)
    data = encode_str(data_orig)
    plain = decrypt(priv, pub, data, enc)
    plain = decompress(plain)
    plain = decode_bytes(plain)
    click.echo(plain)
    print_stats(plain, data_orig)


@click.command(help="Print CW table")
@click.argument("ciphertext_file", type=file_arg)
@soda_options.output_format
@soda_options.column_height
def print_cmd(ciphertext_file: TextIO, output_format: str, column_height: int):
    groups = read_groups(ciphertext_file)
    add_header = output_format == "fixed"
    table = format_table(groups, output_format, column_height, add_header)
    click.echo(table)


@click.command(help="Find error")
@click.argument("ciphertext_file", type=file_arg)
@soda_options.checksum
@soda_options.output_format
@soda_options.column_height
def find_error_cmd(
    ciphertext_file: TextIO, checksum: str, output_format: str, column_height: int
):
    groups = read_groups(ciphertext_file)
    add_header = output_format == "fixed"
    calc = checksum_calculators[checksum]
    error = error_search(groups, calc)
    if error is not None:
        click.echo(f"The error is in: {error}")
        table = format_table(groups, output_format, column_height, add_header, error)
        click.echo(table)
    else:
        click.echo("The file is correct")


cli.add_command(genkey_cmd)
cli.add_command(pubkey_cmd)
cli.add_command(readkey_cmd)
cli.add_command(kdf_cmd)
cli.add_command(encrypt_cmd)
cli.add_command(decrypt_cmd)
cli.add_command(print_cmd)
cli.add_command(find_error_cmd)

if __name__ == "__main__":
    cli()
