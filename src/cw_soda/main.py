from pathlib import Path
from typing import BinaryIO, TextIO

import click
from nacl.public import PrivateKey
from steganon import LSB_MWS, Image

from cw_soda.archivers import archivers, unarchivers
from cw_soda.cryptography import public, secret
from cw_soda.cryptography.kdf import hash_salt, kdf, kdf_profiles
from cw_soda.encoders import RawEncoder, decode_bytes, encoders
from cw_soda.error_search import checksum_calculators, error_search
from cw_soda.format_table import format_table
from cw_soda.io_utils import (
    get_salt,
    init_keypair,
    print_stats,
    read_arg_groups,
    read_bytes,
    read_bytes_formatted,
    read_ciphertext,
    read_groups,
    read_message,
    write_output,
)

text_file = click.File(mode="r", encoding="utf-8", errors="strict")
bin_file = click.File(mode="rb")
in_path = click.Path(dir_okay=False, readable=True, path_type=Path)
out_path = click.Path(dir_okay=False, writable=True, path_type=Path)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="cw-soda")
def cli():
    pass


@click.command()
@click.option("--encoding", default="base36", show_default=True)
def genkey_cmd(encoding: str):
    """Key Generator.

    Encoding: base26 | base31 | base36 | base64 | base94
    """
    enc = encoders[encoding]
    key = PrivateKey.generate().encode(enc)
    click.echo(decode_bytes(key))


@click.command()
@click.argument("private_key_file", type=text_file)
@click.option("--encoding", default="base36", show_default=True)
def pubkey_cmd(private_key_file: TextIO, encoding: str):
    """Get Public Key.

    Encoding: base26 | base31 | base36 | base64 | base94
    """
    enc = encoders[encoding]
    pk = read_bytes_formatted(private_key_file, enc)
    pk = PrivateKey(pk, enc)
    pub = pk.public_key.encode(enc)
    click.echo(decode_bytes(pub))


@click.command()
@click.argument("password_file", type=text_file)
@click.argument("salt_file", type=text_file)
@click.option("--encoding", default="base36", show_default=True)
@click.option("--profile", default="interactive", show_default=True)
@click.option("--raw-salt", is_flag=True, help="Decode the salt as bytes")
def kdf_cmd(
    password_file: TextIO,
    salt_file: TextIO,
    encoding: str,
    profile: str,
    raw_salt: bool,
):
    """Key Derivation Function.

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
@click.argument("private_key_file", type=text_file)
@click.argument("public_key_file", type=text_file)
@click.argument("message_file", type=bin_file)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base36", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def encrypt_cmd(
    private_key_file: TextIO,
    public_key_file: TextIO,
    message_file: BinaryIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Encrypt Message.

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    archiver = archivers[compression]
    data = data_stat = read_message(message_file, data_enc)
    data = archiver(data)
    priv, pub = init_keypair(private_key_file, public_key_file, key_enc)
    encrypted = public.encrypt(priv, pub, data, data_enc)
    write_output(output_file, encrypted, data_enc)
    print_stats(data_stat, encrypted)


@click.command()
@click.argument("key_file", type=text_file)
@click.argument("message_file", type=bin_file)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base36", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def encrypt_secret_cmd(
    key_file: TextIO,
    message_file: BinaryIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Encrypt Message (symmetric).

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    archiver = archivers[compression]
    data = data_stat = read_message(message_file, data_enc)
    data = archiver(data)
    key = read_bytes_formatted(key_file, key_enc)
    encrypted = secret.encrypt(key, data, key_enc, data_enc)
    write_output(output_file, encrypted, data_enc)
    print_stats(data_stat, encrypted)


@click.command()
@click.argument("private_key_file", type=text_file)
@click.argument("public_key_file", type=text_file)
@click.argument("message_file", type=bin_file)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base36", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def decrypt_cmd(
    private_key_file: TextIO,
    public_key_file: TextIO,
    message_file: BinaryIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Decrypt Message.

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    unarchiver = unarchivers[compression]
    data = data_stat = read_ciphertext(message_file, data_enc)
    priv, pub = init_keypair(private_key_file, public_key_file, key_enc)
    plain = public.decrypt(priv, pub, data, data_enc)
    plain = unarchiver(plain)
    write_output(output_file, plain, data_enc)
    print_stats(plain, data_stat)


@click.command()
@click.argument("key_file", type=text_file)
@click.argument("message_file", type=bin_file)
@click.option("--output-file", type=out_path, help="(Optional)")
@click.option("--key-encoding", default="base36", show_default=True)
@click.option("--data-encoding", default="base36", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def decrypt_secret_cmd(
    key_file: TextIO,
    message_file: BinaryIO,
    output_file: Path,
    key_encoding: str,
    data_encoding: str,
    compression: str,
):
    """Decrypt Message (symmetric).

    Key encoding: base26 | base31 | base36 | base64 | base94

    Data encoding: base26 | base31 | base36 | base64 | base94 | binary

    Compression: zlib | bz2 | lzma | raw
    """
    key_enc = encoders[key_encoding]
    data_enc = encoders[data_encoding]
    unarchiver = unarchivers[compression]
    data = data_stat = read_ciphertext(message_file, data_enc)
    key = read_bytes_formatted(key_file, key_enc)
    plain = secret.decrypt(key, data, key_enc, data_enc)
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
    """Print Table.

    This only works with Base26, Base31, and Base36.

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
    """Find Error.

    This only works with Base26, Base31, and Base36.

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


@click.command()
@click.argument("input_image", type=in_path)
@click.argument("output_image", type=out_path)
@click.argument("files", type=in_path, nargs=-1)
@click.option("--profile", default="interactive", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def hide_secret_cmd(
    input_image: Path,
    output_image: Path,
    files: tuple[Path],
    profile: str,
    compression: str,
):
    """Hide Data (symmetric).

    Files: seed password salt plaintext [seed password salt plaintext]...

    Profile: interactive | moderate | sensitive

    Compression: zlib | bz2 | lzma | raw
    """
    profile = kdf_profiles[profile]
    archiver = archivers[compression]

    args = read_arg_groups(files, 4)
    seeds = [read_bytes(group[0]) for group in args]
    passwords = [read_bytes(group[1]) for group in args]
    hashes = [hash_salt(read_bytes(group[2])) for group in args]
    keys = [kdf(pw, salt, profile, RawEncoder) for pw, salt in zip(passwords, hashes)]
    encrypted = []
    for key, group in zip(keys, args):
        data = archiver(group[3].read_bytes())
        data = secret.encrypt(key, data, RawEncoder, RawEncoder)
        encrypted.append(data)

    image = Image.open(input_image)
    lsb_mws = LSB_MWS(image, seeds)
    groups = len(args)
    for i in range(groups):
        lsb_mws.hide(encrypted[i])
        if i < groups - 1:
            lsb_mws.next()

    lsb_mws.finalize()
    if output_image.exists():
        click.confirm(
            f"Overwrite the output file? ({output_image})", default=False, abort=True
        )

    image.save(output_image)


@click.command()
@click.argument("input_image", type=in_path)
@click.argument("files", type=in_path, nargs=-1)
@click.option("--profile", default="interactive", show_default=True)
@click.option("--compression", default="zlib", show_default=True)
def reveal_secret_cmd(
    input_image: Path,
    files: tuple[Path],
    profile: str,
    compression: str,
):
    """Reveal Data (symmetric).

    Files: seed password salt output [seed password salt output]...

    Profile: interactive | moderate | sensitive

    Compression: zlib | bz2 | lzma | raw
    """
    profile = kdf_profiles[profile]
    unarchiver = unarchivers[compression]

    args = read_arg_groups(files, 4)
    seeds = [read_bytes(group[0]) for group in args]
    passwords = [read_bytes(group[1]) for group in args]
    hashes = [hash_salt(read_bytes(group[2])) for group in args]
    keys = [kdf(pw, salt, profile, RawEncoder) for pw, salt in zip(passwords, hashes)]
    outputs = [group[3] for group in args]

    image = Image.open(input_image)
    lsb_mws = LSB_MWS(image, seeds)
    groups = len(args)
    for i in range(groups):
        encrypted = lsb_mws.extract()
        if i < groups - 1:
            lsb_mws.next()

        data = secret.decrypt(keys[i], encrypted, RawEncoder, RawEncoder)
        data = unarchiver(data)
        if outputs[i].exists():
            click.confirm(
                f"Overwrite the output file? ({outputs[i]})", default=False, abort=True
            )

        outputs[i].write_bytes(data)


cli.add_command(genkey_cmd)
cli.add_command(pubkey_cmd)
cli.add_command(kdf_cmd)
cli.add_command(encrypt_cmd)
cli.add_command(encrypt_secret_cmd)
cli.add_command(decrypt_cmd)
cli.add_command(decrypt_secret_cmd)
cli.add_command(print_cmd)
cli.add_command(find_error_cmd)
cli.add_command(hide_secret_cmd)
cli.add_command(reveal_secret_cmd)

if __name__ == "__main__":
    cli()
