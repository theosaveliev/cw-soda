from nacl.encoding import Base16Encoder, Base64Encoder

from .base10_encoder import Base10Encoder
from .base26_encoder import Base26Encoder
from .base31_encoder import Base31Encoder
from .base36_encoder import Base36Encoder
from .base41_encoder import Base41Encoder
from .functions import decode_bytes, encode_key, encode_str

__all__ = [
    "encoders",
    "encode_str",
    "decode_bytes",
    "encode_key",
    "Base10Encoder",
    "Base16Encoder",
    "Base26Encoder",
    "Base31Encoder",
    "Base36Encoder",
    "Base41Encoder",
    "Base64Encoder",
]

encoders = {
    "base10": Base10Encoder,
    "base16": Base16Encoder,
    "base26": Base26Encoder,
    "base31": Base31Encoder,
    "base36": Base36Encoder,
    "base41": Base41Encoder,
    "base64": Base64Encoder,
}
