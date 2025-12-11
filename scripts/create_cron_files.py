from pathlib import Path

cron_dir = Path("cron")
scripts_dir = Path("scripts")

cron_dir.mkdir(exist_ok=True)
scripts_dir.mkdir(exist_ok=True)

# -------------------------------
# Create cron/2fa-cron with LF
# -------------------------------
cron_file = cron_dir / "2fa-cron"

cron_content = "* * * * * cd /app && /opt/venv/bin/python /app/scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1\n"

cron_file.write_text(cron_content, newline="\n")  # force LF line endings


# -------------------------------
# Create scripts/log_2fa_cron.py
# -------------------------------
script_file = scripts_dir / "log_2fa_cron.py"

script_content = """#!/usr/bin/env python3
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
"""

script_file.write_text(script_content, newline="\n")  # force LF


# -------------------------------
# Update .gitattributes
# -------------------------------
gitattributes = Path(".gitattributes")
gitattributes.write_text("cron/2fa-cron text eol=lf\n", newline="\n")

print("Created cron/2fa-cron, scripts/log_2fa_cron.py, and .gitattributes with LF endings.")
