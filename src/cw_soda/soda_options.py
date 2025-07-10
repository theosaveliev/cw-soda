"""CLI options.

The module provides Click decorator Groups to reuse them in the Commands
"""

from types import SimpleNamespace

import click
from click_option_group import MutuallyExclusiveOptionGroup, optgroup

__all__ = ["soda_options"]

soda_options = SimpleNamespace()
option = optgroup.option


def apply_encoding_options(func):
    func = option("--base94", "encoding", is_flag=True, flag_value="base94")(func)
    func = option("--base64", "encoding", is_flag=True, flag_value="base64")(func)
    func = option("--base41", "encoding", is_flag=True, flag_value="base41")(func)
    func = option(
        "--base36",
        "encoding",
        is_flag=True,
        flag_value="base36",
        default=True,
        help="(default)",
    )(func)
    func = option("--base31", "encoding", is_flag=True, flag_value="base31")(func)
    func = option("--base26", "encoding", is_flag=True, flag_value="base26")(func)
    func = option("--base16", "encoding", is_flag=True, flag_value="base16")(func)
    func = option("--base10", "encoding", is_flag=True, flag_value="base10")(func)
    func = optgroup.group("Encoding", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.encoding = apply_encoding_options


def apply_in_encoding_options(func):
    func = option("--in-base94", "in_encoding", is_flag=True, flag_value="base94")(func)
    func = option("--in-base64", "in_encoding", is_flag=True, flag_value="base64")(func)
    func = option("--in-base41", "in_encoding", is_flag=True, flag_value="base41")(func)
    func = option(
        "--in-base36",
        "in_encoding",
        is_flag=True,
        flag_value="base36",
        default=True,
        help="(default)",
    )(func)
    func = option("--in-base31", "in_encoding", is_flag=True, flag_value="base31")(func)
    func = option("--in-base26", "in_encoding", is_flag=True, flag_value="base26")(func)
    func = option("--in-base16", "in_encoding", is_flag=True, flag_value="base16")(func)
    func = option("--in-base10", "in_encoding", is_flag=True, flag_value="base10")(func)
    func = optgroup.group("Input encoding", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.in_encoding = apply_in_encoding_options


def apply_out_encoding_options(func):
    func = option("--out-base94", "out_encoding", is_flag=True, flag_value="base94")(
        func
    )
    func = option("--out-base64", "out_encoding", is_flag=True, flag_value="base64")(
        func
    )
    func = option("--out-base41", "out_encoding", is_flag=True, flag_value="base41")(
        func
    )
    func = option(
        "--out-base36",
        "out_encoding",
        is_flag=True,
        flag_value="base36",
        default=True,
        help="(default)",
    )(func)
    func = option("--out-base31", "out_encoding", is_flag=True, flag_value="base31")(
        func
    )
    func = option("--out-base26", "out_encoding", is_flag=True, flag_value="base26")(
        func
    )
    func = option("--out-base16", "out_encoding", is_flag=True, flag_value="base16")(
        func
    )
    func = option("--out-base10", "out_encoding", is_flag=True, flag_value="base10")(
        func
    )
    func = optgroup.group("Output encoding", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.out_encoding = apply_out_encoding_options


def apply_compression_options(func):
    func = option(
        "--uncompressed", "compression", is_flag=True, flag_value="uncompressed"
    )(func)
    func = option("--lzma", "compression", is_flag=True, flag_value="lzma")(func)
    func = option("--bz2", "compression", is_flag=True, flag_value="bz2")(func)
    func = option(
        "--zlib",
        "compression",
        is_flag=True,
        flag_value="zlib",
        default=True,
        help="(default)",
    )(func)
    func = optgroup.group("Compression", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.compression = apply_compression_options


def apply_output_format_options(func):
    func = option("--csv", "output_format", is_flag=True, flag_value="csv")(func)
    func = option(
        "--fixed",
        "output_format",
        is_flag=True,
        flag_value="fixed",
        default=True,
        help="(default)",
    )(func)
    func = optgroup.group("Output format", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.output_format = apply_output_format_options


def apply_column_height_option(func):
    func = click.option("--column-height", type=int, default=10, help="default=10")(
        func
    )
    return func


soda_options.column_height = apply_column_height_option


def apply_checksum_options(func):
    func = option("--crc32", "checksum", is_flag=True, flag_value="crc32")(func)
    func = option("--crc16", "checksum", is_flag=True, flag_value="crc16")(func)
    func = option(
        "--crc8",
        "checksum",
        is_flag=True,
        flag_value="crc8",
        default=True,
        help="(default)",
    )(func)
    func = optgroup.group("Checksum", cls=MutuallyExclusiveOptionGroup)(func)
    return func


soda_options.checksum = apply_checksum_options


def apply_raw_salt_option(func):
    func = click.option(
        "--raw-salt",
        is_flag=True,
        help="Decode the salt as bytes",
    )(func)
    return func


soda_options.raw_salt = apply_raw_salt_option
