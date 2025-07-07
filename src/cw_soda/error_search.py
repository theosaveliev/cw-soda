import click
from crc import Calculator, Crc8, Crc16, Crc32

from cw_soda.encoders import encode_str

__all__ = ["error_search", "checksum_calculators"]

checksum_calculators = {
    "crc8": Calculator(Crc8.CCITT),
    "crc16": Calculator(Crc16.X25),
    "crc32": Calculator(Crc32.POSIX),
}


def error_search(lines: list, calc: Calculator):
    if len(lines) == 0:
        return None

    if len(lines) == 1:
        return lines[0]

    mid = len(lines) // 2
    left = lines[:mid]
    right = lines[mid:]
    left_sum = calc.checksum([encode_str(ln) for ln in left])
    right_sum = calc.checksum([encode_str(ln) for ln in right])

    click.echo(f"Checksum: {left_sum:X}")
    if click.confirm("Is it correct?", default=None):
        click.echo(f"Checksum: {right_sum:X}")
        if click.confirm("Is it correct?", default=None):
            return None

        return error_search(right, calc)
    return error_search(left, calc)
