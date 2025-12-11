from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.crypto_utils import load_private_key, decrypt_seed, save_seed_to_file, SEED_FILE_PATH


def main():
    encrypted_path = Path("encrypted_seed.txt")
    if not encrypted_path.exists():
        raise FileNotFoundError("encrypted_seed.txt not found. Run request_seed.py first.")

    encrypted_seed_b64 = encrypted_path.read_text().strip()

    private_key = load_private_key("student_private.pem")

    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    print(f"Decrypted hex seed: {hex_seed}")
    print(f"Length: {len(hex_seed)} characters")

    # Save to seed file (for local dev this will be ./data/seed.txt)
    save_seed_to_file(hex_seed)
    print(f"Seed saved to: {SEED_FILE_PATH.resolve()}")


if __name__ == "__main__":
    main()
