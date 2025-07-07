import itertools
import math
import string

import click

__all__ = ["format_table"]


def yield_letters():
    i = 1
    while True:
        for letters in itertools.product(string.ascii_uppercase, repeat=i):
            yield "".join(letters)

        i += 1


def get_header(columns: int, delimiter: str) -> str:
    result = ""
    letters = yield_letters()
    for _ in range(columns):
        title = next(letters)
        title += " " * (5 - len(title))
        result += f"{title}{delimiter}"

    return result


def highlight_text(output_format: str, text: str) -> str:
    if output_format == "csv":
        return f"*{text}*"

    return click.style(text, bold=True, underline=True)


table_delimiters = {"fixed": "\t", "csv": ";"}


def format_table(
    groups: list,
    output_format: str,
    column_height: int,
    add_header: bool,
    highlight: str = None,
) -> str:
    result = ""
    columns = math.ceil(len(groups) / column_height)
    delimiter = table_delimiters[output_format]

    if add_header:
        header = get_header(columns, delimiter)
        result += f"#{delimiter}{header}\n"

    for row in range(column_height):
        if add_header:
            line = f"{row + 1}{delimiter}"
        else:
            line = ""

        for column in range(columns):
            i = row + column * column_height
            if i >= len(groups):
                break

            cell = groups[i]
            if cell == highlight:
                cell = highlight_text(output_format, cell)

            line += f"{cell}{delimiter}"

        result += f"{line}\n"
    return result
