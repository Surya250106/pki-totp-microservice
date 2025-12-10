from pathlib import Path
import sys
from pathlib import Path

# Add repo root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))


from app.crypto_utils import SEED_FILE_PATH
from app.totp_utils import generate_totp_code, get_seconds_remaining, verify_totp_code


def main():
    seed_path = SEED_FILE_PATH  # for local dev, likely ./data/seed.txt
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed file not found at {seed_path}. Run decrypt_seed_local.py first.")

    hex_seed = seed_path.read_text().strip()

    code = generate_totp_code(hex_seed)
    valid_for = get_seconds_remaining()

    print(f"Current TOTP code: {code}")
    print(f"Valid for (approx) {valid_for} more seconds in this 30s window")

    # Quick self-check: verification should pass for the generated code
    is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    print(f"Self-verification result: {is_valid}")


if __name__ == "__main__":
    main()
