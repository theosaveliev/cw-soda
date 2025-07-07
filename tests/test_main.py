import pytest
from click.testing import CliRunner

from cw_soda.main import cli


@pytest.fixture
def keypair():
    return {
        "private_b36": "1Z8JMO1NZRZ7WD9ZTFJK2WVW0D8KHJDNKNJTNV3GVAVVZZSNJC",
        "private_b64": "T2Tsu+ojEAGzkKz4pCsFGuZ+RYVMZleVJskIl8tshSg=",
        "public_b36": "2SFZ0329VK0KXU9DIXVR9ZSOO94HWUOMG99A3YNN654VSW5ANN",
    }


@pytest.fixture
def password():
    return "qwerty"


@pytest.fixture
def encrypted_password_b36():
    return {
        "uncompressed": "ZRGGHXJ2CCPV0SQG3T5S381CT1GSOL87LNHSZ9720HCP9O2MO847TAZX6W2ZR0"
                        "56XR6CVNW",
        "zlib": "3OU4KNC2FSW5P8TW8Z6U3MRP3M1YSVSB84BPAEBCT16AUFJWYRDEZWM1UK9V7T03PL0M9Y"
                "7D5GBEZ129FIKE",
        "bz2": "LJ3C94N8OON8VEL2C2MMCTMO7PFH4TNP8GZ4ZF9T2M34X6CPQMMZ9QM0PNO666CZF6J0SM3"
               "BH63FCOSKN615BR5KXUFMRHLQJMQVLEBSFZL9W3NKK7WR2XVKX0ID7KA",
        "lzma": "9PEEL2MYUSOXVD3FZWSTEQ6J9OKOSJY2QH6DD6RI9BP8WN3I9I3XJ1TMK1ZB5XK05IDRJC"
                "FTC16XQJPFXQFZ4BUJ2GWEL27GCO5OFHS6R05",
    }


@pytest.fixture
def salt_b36():
    return "8F9ZOOMKH6SCW1HRB7WDS84KZ"


def test_genkey():
    runner = CliRunner()
    encodings = [
        "--base10",
        "--base16",
        "--base26",
        "--base31",
        "--base36",
        "--base41",
        "--base64",
    ]
    for enc in encodings:
        result = runner.invoke(cli, ["genkey", enc])
        assert result.exit_code == 0
        assert len(result.stdout) > 40


def test_pubkey(keypair):
    runner = CliRunner()
    args = ["pubkey", "-", "--base36"]
    result = runner.invoke(cli, args=args, input=keypair["private_b36"])
    assert result.exit_code == 0
    assert result.stdout == keypair["public_b36"] + "\n"


def test_readkey(keypair):
    runner = CliRunner()
    args = ["readkey", "-", "--in-base36", "--out-base64"]
    result = runner.invoke(cli, args=args, input=keypair["private_b36"])
    assert result.exit_code == 0
    assert result.stdout == keypair["private_b64"] + "\n"


def test_kdf(password, salt_b36, keypair):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("password_file", "w", encoding="utf-8") as fd:
            fd.write(password)

        args = ["kdf", "password_file", "-", "--base36"]
        result = runner.invoke(cli, args=args, input=salt_b36)
        assert result.exit_code == 0
        assert result.stdout == keypair["private_b36"] + "\n"


def test_decrypt(keypair, password, encrypted_password_b36):
    runner = CliRunner()
    pw = encrypted_password_b36
    with runner.isolated_filesystem():
        with open("priv_file", "w", encoding="utf-8") as fd:
            fd.write(keypair["private_b36"])

        with open("pub_file", "w", encoding="utf-8") as fd:
            fd.write(keypair["public_b36"])

        args = ["decrypt", "priv_file", "pub_file", "-", "--base36", "--uncompressed"]
        result = runner.invoke(cli, args=args, input=pw["uncompressed"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args = ["decrypt", "priv_file", "pub_file", "-", "--base36", "--zlib"]
        result = runner.invoke(cli, args=args, input=pw["zlib"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args = ["decrypt", "priv_file", "pub_file", "-", "--base36", "--bz2"]
        result = runner.invoke(cli, args=args, input=pw["bz2"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args = ["decrypt", "priv_file", "pub_file", "-", "--base36", "--lzma"]
        result = runner.invoke(cli, args=args, input=pw["lzma"])
        assert result.exit_code == 0
        assert result.stdout == password + "\n"


def test_encrypt(keypair, password):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("priv_file", "w", encoding="utf-8") as fd:
            fd.write(keypair["private_b36"])

        with open("pub_file", "w", encoding="utf-8") as fd:
            fd.write(keypair["public_b36"])

        args = ["encrypt", "priv_file", "pub_file", "-", "--base36", "--uncompressed"]
        result = runner.invoke(cli, args=args, input=password)
        encrypted = result.stdout
        assert result.exit_code == 0

        args = ["decrypt", "priv_file", "pub_file", "-", "--base36", "--uncompressed"]
        result = runner.invoke(cli, args=args, input=encrypted)
        assert result.exit_code == 0
        assert result.stdout == password + "\n"

        args = ["encrypt", "priv_file", "pub_file", "-", "--base36", "--zlib"]
        result = runner.invoke(cli, args=args, input=password)
        assert result.exit_code == 0
        assert len(result.stdout) > 60

        args = ["encrypt", "priv_file", "pub_file", "-", "--base36", "--bz2"]
        result = runner.invoke(cli, args=args, input=password)
        assert result.exit_code == 0
        assert len(result.stdout) > 60

        args = ["encrypt", "priv_file", "pub_file", "-", "--base36", "--lzma"]
        result = runner.invoke(cli, args=args, input=password)
        assert result.exit_code == 0
        assert len(result.stdout) > 60
