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
    """Random salt."""
    return "12345"


@pytest.fixture
def salt_hashed():
    """The salt's hash."""
    return "3AIK26Z5MZ294C6SN7WV21X"


@pytest.fixture
def private_key():
    """The key derived from the password and salt."""
    return "8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP"


@pytest.fixture
def public_key():
    """The Public key for the Private key."""
    return "MXRJI9V1X0J83N4UCOYLJ091F1KOS9XOEGCKIG7KPXTVZUQRQ"


@pytest.fixture
def encrypted_public():
    """The password encrypted with the Public module."""
    return "1BELDG5XZ7GDBS48H5NATGAXPUOITZR0X48RNGV2UALN7JLC88NOCQSQJPMV94AB41G4HCIM"


@pytest.fixture
def encrypted_secret():
    """The password encrypted with the Secret module."""
    return "54N2ZP3PH56LVV2K2GLW6AK7PALBZ1VDHP7DXPRHM061WVA1K8HOAY3T4ELX6L671L0KOM2"


def test_genkey():
    runner = CliRunner()
    text_encoders = ["base26", "base31", "base36", "base64", "base94"]
    for enc in text_encoders:
        result = runner.invoke(cli, ["genkey", "--encoding", enc])
        assert result.exit_code == 0
        assert len(result.stdout) > 30


def test_pubkey(private_key, public_key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private_key", "w", encoding="utf-8") as fd:
            fd.write(private_key)

        args = ["pubkey", "private_key", "--encoding", "base36"]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == public_key + "\n"


def test_kdf_plain(password, salt, private_key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("password", "w", encoding="utf-8") as fd:
            fd.write(password)

        with open("salt", "w", encoding="utf-8") as fd:
            fd.write(salt)

        args = [
            "kdf",
            "password",
            "salt",
            "--encoding",
            "base36",
            "--profile",
            "interactive",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == private_key + "\n"


def test_kdf_hash(password, salt_hashed, private_key):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("password", "w", encoding="utf-8") as fd:
            fd.write(password)

        with open("salt", "w", encoding="utf-8") as fd:
            fd.write(salt_hashed)

        args = [
            "kdf",
            "password",
            "salt",
            "--encoding",
            "base36",
            "--profile",
            "interactive",
            "--raw-salt",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == private_key + "\n"


def test_decrypt_public(private_key, public_key, encrypted_public, password):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private_key", "w", encoding="utf-8") as fd:
            fd.write(private_key)

        with open("public_key", "w", encoding="utf-8") as fd:
            fd.write(public_key)

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(encrypted_public)

        args = [
            "decrypt",
            "private_key",
            "public_key",
            "message",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_decrypt_secret(private_key, encrypted_secret, password):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("secret_key", "w", encoding="utf-8") as fd:
            fd.write(private_key)

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(encrypted_secret)

        args = [
            "decrypt-secret",
            "secret_key",
            "message",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt_public(private_key, public_key, password):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("private_key", "w", encoding="utf-8") as fd:
            fd.write(private_key)

        with open("public_key", "w", encoding="utf-8") as fd:
            fd.write(public_key)

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt",
            "private_key",
            "public_key",
            "message",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
            "--output-file",
            "encrypted",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0

        args = [
            "decrypt",
            "private_key",
            "public_key",
            "encrypted",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt_secret(private_key, password):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("secret_key", "w", encoding="utf-8") as fd:
            fd.write(private_key)

        with open("message", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = [
            "encrypt-secret",
            "secret_key",
            "message",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
            "--output-file",
            "encrypted",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0

        args = [
            "decrypt-secret",
            "secret_key",
            "encrypted",
            "--key-encoding",
            "base36",
            "--data-encoding",
            "base36",
            "--compression",
            "raw",
        ]
        result = runner.invoke(cli, args=args)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"
