import bz2
import lzma
import zlib

__all__ = ["archivers", "unarchivers"]


def compress_zlib(data: bytes) -> bytes:
    return zlib.compress(data, level=9)


def compress_bz2(data: bytes) -> bytes:
    return bz2.compress(data, compresslevel=9)


def compress_lzma(data: bytes) -> bytes:
    return lzma.compress(
        data,
        format=lzma.FORMAT_ALONE,
        check=lzma.CHECK_NONE,
        preset=lzma.PRESET_EXTREME,
    )


def decompress_zlib(data: bytes) -> bytes:
    return zlib.decompress(data)


def decompress_bz2(data: bytes) -> bytes:
    return bz2.decompress(data)


def decompress_lzma(data: bytes) -> bytes:
    return lzma.decompress(data, format=lzma.FORMAT_ALONE)


def noop(data):
    return data


archivers = {
    "zlib": compress_zlib,
    "bz2": compress_bz2,
    "lzma": compress_lzma,
    "raw": noop,
}

unarchivers = {
    "zlib": decompress_zlib,
    "bz2": decompress_bz2,
    "lzma": decompress_lzma,
    "raw": noop,
}
