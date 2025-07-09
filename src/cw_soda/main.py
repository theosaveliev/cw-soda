from typing import TextIO

import click
from nacl.public import PrivateKey

from cw_soda.archivers import archivers, unarchivers
from cw_soda.cryptography import public, secret
from cw_soda.encoders import decode_bytes, encode_data, encode_key, encode_str, encoders
from cw_soda.error_search import checksum_calculators, error_search
from cw_soda.format_table import format_table
from cw_soda.io_utils import (
    get_salt,
    init_keypair,
    print_salt,
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


@click.command(help="Generate a Private or a Secret Key")
@soda_options.encoding
@click.option("--symmetric", is_flag=True)
def genkey_cmd(encoding: str, symmetric: bool):
    enc = encoders[encoding]
    if symmetric:
        key = encode_data(secret.generate_key(), enc)
    else:
        key = encode_key(PrivateKey.generate(), enc)

    click.echo(key)


@click.command(help="Get the Public Key")
@click.argument("private_key_file", type=file_arg)
@soda_options.encoding
def pubkey_cmd(private_key_file: TextIO, encoding: str):
    enc = encoders[encoding]
    pk = read_bytes(private_key_file)
    pk = PrivateKey(pk, enc)
    pub = encode_key(pk.public_key, enc)
    click.echo(pub)


@click.command(help="Read a Private or a Secret Key")
@click.argument("key_file", type=file_arg)
@soda_options.in_encoding
@soda_options.out_encoding
@click.option("--symmetric", is_flag=True)
def readkey_cmd(key_file: TextIO, in_encoding: str, out_encoding: str, symmetric: bool):
    in_enc = encoders[in_encoding]
    out_enc = encoders[out_encoding]
    key = read_bytes(key_file)
    if symmetric:
        key = in_enc.decode(key)
        key = encode_data(key, out_enc)
    else:
        key = PrivateKey(key, in_enc)
        key = encode_key(key, out_enc)

    click.echo(key)


@click.command(help="Derive a Private or a Secret Key")
@click.argument("password_file", type=file_arg)
@click.argument("salt_file", type=file_arg, required=False)
@soda_options.encoding
@soda_options.hash_salt_opt
@click.option("--symmetric", is_flag=True)
def kdf_cmd(
    password_file: TextIO,
    salt_file: TextIO,
    encoding: str,
    hash_salt_opt: bool,
    symmetric: bool,
):
    enc = encoders[encoding]
    password = read_bytes(password_file)
    salt = get_salt(salt_file, enc, hash_salt_opt)
    print_salt(salt, enc)
    if symmetric:
        key = secret.kdf(password, salt, enc)
    else:
        key = public.kdf(password, salt, enc)

    key = decode_bytes(key)
    click.echo(key)


@click.command(help="Encrypt the message")
@click.argument("message_file", type=file_arg)
@click.argument("private_or_secret_key_file", type=file_arg)
@click.argument("public_key_file", type=file_arg, required=False)
@soda_options.encoding
@soda_options.compression
@click.option("--symmetric", is_flag=True)
def encrypt_cmd(
    message_file: TextIO,
    private_or_secret_key_file: TextIO,
    public_key_file: TextIO,
    encoding: str,
    compression: str,
    symmetric: bool,
):
    enc = encoders[encoding]
    compress = archivers[compression]
    data_orig = read_str(message_file)
    data = encode_str(data_orig)
    data = compress(data)
    if symmetric:
        key = read_bytes(private_or_secret_key_file)
        encrypted = secret.encrypt(key, data, enc)
    else:
        priv, pub = init_keypair(private_or_secret_key_file, public_key_file, enc)
        encrypted = public.encrypt(priv, pub, data, enc)

    encrypted = decode_bytes(encrypted)
    click.echo(encrypted)
    print_stats(data_orig, encrypted)


@click.command(help="Decrypt the message")
@click.argument("message_file", type=file_arg)
@click.argument("private_or_secret_key_file", type=file_arg)
@click.argument("public_key_file", type=file_arg, required=False)
@soda_options.encoding
@soda_options.compression
@click.option("--symmetric", is_flag=True)
def decrypt_cmd(
    message_file: TextIO,
    private_or_secret_key_file: TextIO,
    public_key_file: TextIO,
    encoding: str,
    compression: str,
    symmetric: bool,
):
    enc = encoders[encoding]
    decompress = unarchivers[compression]
    data = read_str(message_file)
    data_orig = remove_whitespace(data)
    data = encode_str(data_orig)
    if symmetric:
        key = read_bytes(private_or_secret_key_file)
        plain = secret.decrypt(key, data, enc)
    else:
        priv, pub = init_keypair(private_or_secret_key_file, public_key_file, enc)
        plain = public.decrypt(priv, pub, data, enc)

    plain = decompress(plain)
    plain = decode_bytes(plain)
    click.echo(plain)
    print_stats(plain, data_orig)


@click.command(help="Print as table")
@click.argument("ciphertext_file", type=file_arg)
@soda_options.output_format
@soda_options.column_height
def print_cmd(ciphertext_file: TextIO, output_format: str, column_height: int):
    groups = read_groups(ciphertext_file)
    add_header = output_format == "fixed"
    table = format_table(groups, output_format, column_height, add_header)
    click.echo(table)


@click.command(help="Find the error")
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
