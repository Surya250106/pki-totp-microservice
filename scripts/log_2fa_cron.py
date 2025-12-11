#!/usr/bin/env python3
import sys
import os
sys.path.append("/app")
from datetime import datetime
import sys
from pathlib import Path

try:
    from app.crypto_utils import SEED_FILE_PATH
    from app.totp_utils import generate_totp_code
except Exception as e:
    print(f"Import error in cron script: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    seed_path = Path(SEED_FILE_PATH)
    now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if not seed_path.exists():
        print(f"{now_utc} - ERROR: seed file not found at {seed_path}", file=sys.stderr)
        return

    try:
        hex_seed = seed_path.read_text().strip()
        code = generate_totp_code(hex_seed)
        print(f"{now_utc} - 2FA Code: {code}")
    except Exception as e:
        print(f"{now_utc} - ERROR generating TOTP: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
