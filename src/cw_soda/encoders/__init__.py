from nacl.encoding import Base64Encoder, RawEncoder

from .base26_encoder import Base26Encoder
from .base31_encoder import Base31Encoder
from .base36_encoder import Base36Encoder
from .base94_encoder import Base94Encoder
from .functions import decode_bytes, encode_str

__all__ = [
    "encoders",
    "encode_str",
    "decode_bytes",
    "Base26Encoder",
    "Base31Encoder",
    "Base36Encoder",
    "Base64Encoder",
    "Base94Encoder",
    "RawEncoder",
]

encoders = {
    "base26": Base26Encoder,
    "base31": Base31Encoder,
    "base36": Base36Encoder,
    "base64": Base64Encoder,
    "base94": Base94Encoder,
    "binary": RawEncoder,
}
