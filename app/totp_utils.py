import base64
import time
from typing import Tuple

import pyotp

from .crypto_utils import validate_hex_seed


def _hex_to_base32_seed(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 string for TOTP.

    Steps:
    1. Validate hex seed
    2. Convert hex -> bytes
    3. Base32-encode bytes
    """
    hex_seed = hex_seed.strip()
    validate_hex_seed(hex_seed)

    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.

    Config:
      - Algorithm: SHA-1 (pyotp default)
      - Period: 30 seconds
      - Digits: 6
    """
    base32_seed = _hex_to_base32_seed(hex_seed)
    totp = pyotp.TOTP(base32_seed)  # default: SHA1, 30s, 6 digits
    code = totp.now()
    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance.

    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: ± window in number of periods (default 1 = ±30s)

    Returns:
        True if code is valid in [t-1, t, t+1] periods, else False.
    """
    if not code or not code.isdigit() or len(code) != 6:
        return False

    base32_seed = _hex_to_base32_seed(hex_seed)
    totp = pyotp.TOTP(base32_seed)

    # valid_window = 1 => allow one step before and after
    return totp.verify(code, valid_window=valid_window)


def get_seconds_remaining(period: int = 30) -> int:
    """
    Get remaining seconds in the current TOTP period.

    For example, if period=30:
      - returns 29 at the start of a window
      - down to 0 at the end
    """
    now = int(time.time())
    return period - (now % period) - 1
