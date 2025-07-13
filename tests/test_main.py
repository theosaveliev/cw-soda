# pylint: disable=redefined-outer-name
import pytest
from click.testing import CliRunner

from cw_soda.main import cli


@pytest.fixture
def password():
    """Random password."""
    return "qwerty"


@pytest.fixture
def salt():
    """Random salt and it's hash."""
    return {"plain": "12345", "hash": "3AIK26Z5MZ294C6SN7WV21X"}


@pytest.fixture
def key():
    """The key derived from the password and salt, and the corresponding public key."""
    return {
        "private36": "8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP",
        "private64": "CUs6rt6wYOVzrlmUCRaPaFuZUV1V+p2SeOeBCnlDat0=",
        "public36": "MXRJI9V1X0J83N4UCOYLJ091F1KOS9XOEGCKIG7KPXTVZUQRQ",
    }


@pytest.fixture
def encrypted_public():
    """The password encrypted with the Public module."""
    return {
        "raw": "1BELDG5XZ7GDBS48H5NATGAXPUOITZR0X48RNGV2UALN7JLC88NOCQSQJPMV94AB41G4HCI"
        "M",
        "zlib": "4CAXMJM3ULPX7BCR8O20M3G9GFNZBPBYRKDQK4NM6PWGRLPDCIFBLHXBFGLRGCZIP19MDN"
        "PJMC2V3RK8KIHX",
        "bz2": "MDUC9F8RZNC2XCIXE67T5OPSXGGYU8A8DGJ2ANC0BJ990KR09FS73T1PVX8HICH6R8SIHOS"
        "9SG1TVJG7Q31KZRFI3NAT3MFNGBHPDCVW4XFA97N695YQTCT0NSBDQGG",
        "lzma": "AP1OLWB5YKYI6K6YY3G13KGCU28OEXRXZP251VIYQVLAVFGHXGPK30E1XBWUGRQZWK1HCY"
        "2MU8B1K5AD3DDTGQCI8SI43F5T2EQGHE867V5",
    }


@pytest.fixture
def encrypted_secret():
    """The password encrypted with the Secret module."""
    return {
        "raw": "54N2ZP3PH56LVV2K2GLW6AK7PALBZ1VDHP7DXPRHM061WVA1K8HOAY3T4ELX6L671L0KOM2"
    }


def test_genkey():
    runner = CliRunner()
    text_encoders = ["base26", "base31", "base36", "base64", "base94"]
    for enc in text_encoders:
        result = runner.invoke(cli, ["genkey", "--encoding", enc])
        assert result.exit_code == 0
        assert len(result.stdout) > 30


def test_pubkey(key):
    runner = CliRunner()
    args = ["pubkey", "-", "--encoding", "base36"]
    result = runner.invoke(cli, args=args, input=key["private36"])
    assert result.exit_code == 0
    assert result.stdout == key["public36"] + "\n"


def test_kdf_plain(password, salt, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("password", "w", encoding="utf-8") as fd:
            fd.write(password)

        with open("salt", "w", encoding="utf-8") as fd:
            fd.write(salt["plain"])

        args = ["kdf", "password", "salt", "--encoding", "base36"]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == key["private36"] + "\n"


def test_kdf_hash(password, salt, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("password", "w", encoding="utf-8") as fd:
            fd.write(password)

        with open("salt", "w", encoding="utf-8") as fd:
            fd.write(salt["hash"])

        args = ["kdf", "password", "salt", "--encoding", "base36", "--raw-salt"]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == key["private36"] + "\n"


def test_decrypt_public(password, key, encrypted_public):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("public", "w", encoding="utf-8") as fd:
            fd.write(key["public36"])

        args = [
            "decrypt",
            "-",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args, input=encrypted_public["raw"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args.pop()
        args.append("zlib")
        result = runner.invoke(cli, args=args, input=encrypted_public["zlib"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args.pop()
        args.append("bz2")
        result = runner.invoke(cli, args=args, input=encrypted_public["bz2"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args.pop()
        args.append("lzma")
        result = runner.invoke(cli, args=args, input=encrypted_public["lzma"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_decrypt_secret(password, key, encrypted_secret):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("public", "w", encoding="utf-8") as fd:
            fd.write(key["public36"])

        args = [
            "decrypt",
            "-",
            "private",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args, input=encrypted_secret["raw"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt_public(password, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("public", "w", encoding="utf-8") as fd:
            fd.write(key["public36"])

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt",
            "message",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        encrypted = result.stdout

        args = [
            "decrypt",
            "-",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args, input=encrypted)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt_secret(password, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt",
            "message",
            "private",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        encrypted = result.stdout

        args = [
            "decrypt",
            "-",
            "private",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args, input=encrypted)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt_public_binary(password, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("public", "w", encoding="utf-8") as fd:
            fd.write(key["public36"])

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt",
            "message",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "binary",
            "--compression",
            "raw",
            "--output-file",
            "encrypt_output",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0

        args = [
            "decrypt",
            "encrypt_output",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "binary",
            "--compression",
            "raw",
            "--output-file",
            "decrypt_output",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0

        with open("decrypt_output", "rt", encoding="utf-8") as fd:
            assert fd.read() == password


def test_encrypt_public_compression(password, key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private", "w", encoding="utf-8") as fd:
            fd.write(key["private36"])

        with open("public", "w", encoding="utf-8") as fd:
            fd.write(key["public36"])

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt",
            "message",
            "private",
            "public",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "zlib",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert len(result.stdout) > 60

        args.pop()
        args.append("bz2")
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert len(result.stdout) > 60

        args.pop()
        args.append("lzma")
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert len(result.stdout) > 60
