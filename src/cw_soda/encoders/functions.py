from nacl.encoding import Encodable, Encoder

__all__ = ["encode_str", "decode_bytes", "encode_key"]


def encode_str(data: str) -> bytes:
    return data.encode(encoding="utf-8", errors="strict")


def decode_bytes(data: bytes) -> str:
    return data.decode(encoding="utf-8", errors="strict")


def encode_key(key: Encodable, encoder: Encoder) -> str:
    return decode_bytes(key.encode(encoder))


def int_to_base(number: int, alphabet: str) -> str:
    result = []
    base = len(alphabet)
    abs_number = abs(number)
    while abs_number:
        abs_number, remainder = divmod(abs_number, base)
        result.append(alphabet[remainder])

    if number < 0:
        result.append("-")

    return "".join(reversed(result))


def base_to_int(source: str, alphabet: str) -> int:
    number = 0
    base = len(alphabet)
    for index, digit in enumerate(reversed(source)):
        number += alphabet.index(digit) * (base**index)

    return number


def bytes_to_base(source: bytes, alphabet: str) -> str:
    return int_to_base(int.from_bytes(source), alphabet)


def int_to_bytes(number: int) -> bytes:
    buffer = bytearray()
    while number:
        buffer.append(number & 0xFF)
        number //= 256

    buffer.reverse()
    return bytes(buffer)


def base_to_bytes(source: str, alphabet: str) -> bytes:
    return int_to_bytes(base_to_int(source, alphabet))
