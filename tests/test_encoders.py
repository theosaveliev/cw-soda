from cw_soda.encoders import (
    Base10Encoder,
    Base16Encoder,
    Base26Encoder,
    Base31Encoder,
    Base36Encoder,
    Base41Encoder,
    Base64Encoder,
)


def test_encoders():
    assert Base10Encoder.encode(b"\x64") == b"100"
    assert Base10Encoder.decode(b"100") == b"\x64"

    assert Base16Encoder.encode(b"\x64") == b"64"
    assert Base16Encoder.decode(b"64") == b"\x64"

    assert Base26Encoder.encode(b"\x64") == b"DW"
    assert Base26Encoder.decode(b"DW") == b"\x64"

    one_hundred_b31 = "ГЗ".encode(encoding="utf-8")
    assert Base31Encoder.encode(b"\x64") == one_hundred_b31
    assert Base31Encoder.decode(one_hundred_b31) == b"\x64"

    assert Base36Encoder.encode(b"\x64") == b"2S"
    assert Base36Encoder.decode(b"2S") == b"\x64"

    one_hundred_b41 = "2и".encode(encoding="utf-8")
    assert Base41Encoder.encode(b"\x64") == one_hundred_b41
    assert Base41Encoder.decode(one_hundred_b41) == b"\x64"

    assert Base64Encoder.encode(b"\x64") == b"ZA=="
    assert Base64Encoder.decode(b"ZA==") == b"\x64"
