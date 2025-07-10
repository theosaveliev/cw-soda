from typing import TextIO

import click
from nacl.public import PrivateKey

from cw_soda.archivers import archivers, unarchivers
from cw_soda.cryptography import public, secret
from cw_soda.encoders import decode_bytes, encode_str, encoders
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


@click.command(help="Generate Private Key")
@soda_options.encoding
def genkey_cmd(encoding: str):
    enc = encoders[encoding]
    key = PrivateKey.generate().encode(enc)
    click.echo(decode_bytes(key))


@click.command(help="Get Public Key")
@click.argument("private_key", type=file_arg)
@soda_options.encoding
def pubkey_cmd(private_key: TextIO, encoding: str):
    enc = encoders[encoding]
    pk = read_bytes(private_key)
    pk = PrivateKey(pk, enc)
    pub = pk.public_key.encode(enc)
    click.echo(decode_bytes(pub))


@click.command(help="Encode file")
@click.argument("file", type=file_arg)
@soda_options.in_encoding
@soda_options.out_encoding
def encode_cmd(file: TextIO, in_encoding: str, out_encoding: str):
    in_enc = encoders[in_encoding]
    out_enc = encoders[out_encoding]
    key = read_bytes(file)
    key = in_enc.decode(key)
    key = out_enc.encode(key)
    key = decode_bytes(key)
    click.echo(key)


@click.command(help="Derive Private Key")
@click.argument("password", type=file_arg)
@click.argument("salt", type=file_arg, required=False)
@soda_options.encoding
@soda_options.raw_salt
def kdf_cmd(password: TextIO, salt: TextIO, encoding: str, raw_salt: bool):
    enc = encoders[encoding]
    password = read_bytes(password)
    salt = get_salt(salt, raw_salt, enc)
    print_salt(salt, enc)
    key = public.kdf(password, salt, enc)
    key = decode_bytes(key)
    click.echo(key)


@click.command(help="Encrypt message")
@click.argument("message", type=file_arg)
@click.argument("private_key", type=file_arg)
@click.argument("public_key", type=file_arg, required=False)
@soda_options.encoding
@soda_options.compression
def encrypt_cmd(
    message: TextIO,
    private_key: TextIO,
    public_key: TextIO,
    encoding: str,
    compression: str,
):
    enc = encoders[encoding]
    compress = archivers[compression]
    data = data_stat = read_str(message)
    data = encode_str(data)
    data = compress(data)
    if public_key is None:
        key = read_bytes(private_key)
        encrypted = secret.encrypt(key, data, enc)
    else:
        priv, pub = init_keypair(private_key, public_key, enc)
        encrypted = public.encrypt(priv, pub, data, enc)

    encrypted = decode_bytes(encrypted)
    click.echo(encrypted)
    print_stats(data_stat, encrypted)


@click.command(help="Decrypt message")
@click.argument("message", type=file_arg)
@click.argument("private_key", type=file_arg)
@click.argument("public_key", type=file_arg, required=False)
@soda_options.encoding
@soda_options.compression
def decrypt_cmd(
    message: TextIO,
    private_key: TextIO,
    public_key: TextIO,
    encoding: str,
    compression: str,
):
    enc = encoders[encoding]
    decompress = unarchivers[compression]
    data = read_str(message)
    data = data_stat = remove_whitespace(data)
    data = encode_str(data)
    if public_key is None:
        key = read_bytes(private_key)
        plain = secret.decrypt(key, data, enc)
    else:
        priv, pub = init_keypair(private_key, public_key, enc)
        plain = public.decrypt(priv, pub, data, enc)

    plain = decompress(plain)
    plain = decode_bytes(plain)
    click.echo(plain)
    print_stats(plain, data_stat)


@click.command(help="Print table")
@click.argument("message", type=file_arg)
@soda_options.output_format
@soda_options.column_height
@click.option("--no-header", is_flag=True)
def print_cmd(message: TextIO, output_format: str, column_height: int, no_header: bool):
    add_header = not no_header
    groups = read_groups(message)
    table = format_table(groups, output_format, column_height, add_header)
    click.echo(table)


@click.command(help="Find error")
@click.argument("message", type=file_arg)
@soda_options.checksum
@soda_options.output_format
@soda_options.column_height
@click.option("--no-header", is_flag=True)
def find_error_cmd(
    message: TextIO,
    checksum: str,
    output_format: str,
    column_height: int,
    no_header: bool,
):
    add_header = not no_header
    calc = checksum_calculators[checksum]
    groups = read_groups(message)
    error = error_search(groups, calc)
    if error is not None:
        click.echo(f"The error is in: {error}")
        table = format_table(groups, output_format, column_height, add_header, error)
        click.echo(table)
    else:
        click.echo("The file is correct")


cli.add_command(genkey_cmd)
cli.add_command(pubkey_cmd)
cli.add_command(encode_cmd)
cli.add_command(kdf_cmd)
cli.add_command(encrypt_cmd)
cli.add_command(decrypt_cmd)
cli.add_command(print_cmd)
cli.add_command(find_error_cmd)

if __name__ == "__main__":
    cli()
