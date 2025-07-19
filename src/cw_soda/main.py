from pathlib import Path
from typing import BinaryIO, TextIO

import click
from nacl.public import PrivateKey

from cw_soda.archivers import archivers, unarchivers
from cw_soda.cryptography import public, secret
from cw_soda.cryptography.kdf import kdf, kdf_profiles
from cw_soda.encoders import decode_bytes, encoders
from cw_soda.error_search import checksum_calculators, error_search
from cw_soda.format_table import format_table
from cw_soda.io_utils import (
    get_salt,
    init_keypair,
    print_stats,
    read_bytes,
    read_ciphretext,
    read_groups,
    read_message,
    write_output,
)

text_file = click.File(mode="r", encoding="utf-8", errors="strict")
bin_file = click.File(mode="rb")
out_path = click.Path(dir_okay=False, writable=True, path_type=Path)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="cw-soda")
def cli():
    pass


@click.command()
@click.option("--encoding", default="base64", show_default=True)
def genkey_cmd(encoding: str):
    """Generate Private Key.

    Encoding: base26 | base31 | base36 | base64 | base94
    """
    enc = encoders[encoding]
    key = PrivateKey.generate().encode(enc)
    click.echo(decode_bytes(key))


@click.command()
@click.argument("private_key_file", type=text_file)
@click.option("--encoding", default="base64", show_default=True)
def pubkey_cmd(private_key_file: TextIO, encoding: str):
    """Get Public Key.

    Encoding: base26 | base31 | base36 | base64 | base94
    """
    enc = encoders[encoding]
    pk = read_bytes(private_key_file)
    pk = PrivateKey(pk, enc)
    pub = pk.public_key.encode(enc)
    click.echo(decode_bytes(pub))


@click.command()
@click.argument("password_file", type=text_file)
@click.argument("salt_file", type=text_file)
@click.option("--encoding", default="base64", show_default=True)
@click.option("--profile", default="interactive", show_default=True)
@click.option("--raw-salt", is_flag=True, help="Decode the salt as bytes")
def kdf_cmd(
    password_file: TextIO,
    salt_file: TextIO,
    encoding: str,
    profile: str,
    raw_salt: bool,
):
    """Derive Private Key.

    Encoding: base26 | base31 | base36 | base64 | base94

    Profile: interactive | moderate | sensitive
    """
    enc = encoders[encoding]
    prof = kdf_profiles[profile]
    password = read_bytes(password_file)
    salt = get_salt(salt_file, raw_salt, enc)
    key = kdf(password, salt, prof, enc)
    click.echo(decode_bytes(key))


@click.command()
@click.argument("message_file", type=bin_file)
@click.argument("private_key_file", type=text_file)
@click.argument("public_key_file", type=text_file, required=False)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base64", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def encrypt_cmd(
    message_file: BinaryIO,
    private_key_file: TextIO,
    public_key_file: TextIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Encrypt message.

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    archiver = archivers[compression]
    data = data_stat = read_message(message_file, data_enc)
    data = archiver(data)
    if public_key_file is None:
        key = read_bytes(private_key_file)
        encrypted = secret.encrypt(key, data, key_enc, data_enc)
    else:
        priv, pub = init_keypair(private_key_file, public_key_file, key_enc)
        encrypted = public.encrypt(priv, pub, data, data_enc)

    write_output(output_file, encrypted, data_enc)
    print_stats(data_stat, encrypted)


@click.command()
@click.argument("message_file", type=bin_file)
@click.argument("private_key_file", type=text_file)
@click.argument("public_key_file", type=text_file, required=False)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base64", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def decrypt_cmd(
    message_file: BinaryIO,
    private_key_file: TextIO,
    public_key_file: TextIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Decrypt message.

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    unarchiver = unarchivers[compression]
    data = data_stat = read_ciphretext(message_file, data_enc)
    if public_key_file is None:
        key = read_bytes(private_key_file)
        plain = secret.decrypt(key, data, key_enc, data_enc)
    else:
        priv, pub = init_keypair(private_key_file, public_key_file, key_enc)
        plain = public.decrypt(priv, pub, data, data_enc)

    plain = unarchiver(plain)
    write_output(output_file, plain, data_enc)
    print_stats(plain, data_stat)


@click.command()
@click.argument("message_file", type=text_file)
@click.option("--output-format", default="fixed", show_default=True)
@click.option("--column-height", default=10, show_default=True)
@click.option("--no-header", is_flag=True)
def print_cmd(
    message_file: TextIO, output_format: str, column_height: int, no_header: bool
):
    """Print table.

    Output format: fixed | csv
    """
    add_header = not no_header
    groups = read_groups(message_file)
    table = format_table(groups, output_format, column_height, add_header)
    click.echo(table)


@click.command()
@click.argument("message_file", type=text_file)
@click.option("--checksum", default="crc8", show_default=True)
@click.option("--output-format", default="fixed", show_default=True)
@click.option("--column-height", default=10, show_default=True)
@click.option("--no-header", is_flag=True)
def find_error_cmd(
    message_file: TextIO,
    checksum: str,
    output_format: str,
    column_height: int,
    no_header: bool,
):
    """Find error.

    Checksum: crc8 | crc16 | crc32

    Output format: fixed | csv
    """
    add_header = not no_header
    calc = checksum_calculators[checksum]
    groups = read_groups(message_file)
    error = error_search(groups, calc)
    if error is None:
        click.echo("The file is correct")
    else:
        click.echo(f"The error is in: {error}")
        table = format_table(groups, output_format, column_height, add_header, error)
        click.echo(table)


cli.add_command(genkey_cmd)
cli.add_command(pubkey_cmd)
cli.add_command(kdf_cmd)
cli.add_command(encrypt_cmd)
cli.add_command(decrypt_cmd)
cli.add_command(print_cmd)
cli.add_command(find_error_cmd)

if __name__ == "__main__":
    cli()
