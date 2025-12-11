import base64
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


# Use env var for seed path (good for Docker later).
# Default to a local path for development.
SEED_FILE_PATH = Path(os.getenv("SEED_FILE_PATH", "./data/seed.txt"))


def load_private_key(path: str = "student_private.pem") -> rsa.RSAPrivateKey:
    """
    Load the student's RSA private key from PEM file.
    """
    pem_path = Path(path)
    if not pem_path.exists():
        raise FileNotFoundError(f"Private key file not found: {pem_path}")

    pem_data = pem_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,
    )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Loaded key is not an RSA private key")

    # Optional: validate key size
    if private_key.key_size != 4096:
        raise ValueError(f"Private key size must be 4096 bits, got {private_key.key_size}")

    return private_key


def validate_hex_seed(seed: str) -> None:
    """
    Validate that seed is a 64-character lowercase hex string.
    Raises ValueError if invalid.
    """
    seed = seed.strip()
    if len(seed) != 64:
        raise ValueError(f"Seed must be 64 hex chars, got length {len(seed)}")
    allowed = set("0123456789abcdef")
    if not all(c in allowed for c in seed):
        raise ValueError("Seed contains non-hex characters")
    

def decrypt_seed(encrypted_seed_b64: str, private_key: rsa.RSAPrivateKey) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP-SHA256.

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext
        private_key: RSA private key object

    Returns:
        Decrypted hex seed (64-character string)
    """
    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64.strip())
    except Exception as e:
        raise ValueError(f"Invalid base64 encrypted seed: {e}") from e

    # 2. RSA/OAEP decrypt with SHA-256, MGF1(SHA-256), label=None
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as e:
        # Cryptographic error
        raise ValueError(f"RSA decryption failed: {e}") from e

    # 3. Decode bytes to UTF-8 string
    try:
        seed_str = plaintext_bytes.decode("utf-8").strip()
    except UnicodeDecodeError as e:
        raise ValueError(f"Decrypted seed is not valid UTF-8: {e}") from e

    # 4. Validate 64-char hex seed
    validate_hex_seed(seed_str)

    return seed_str


def save_seed_to_file(seed_hex: str, path: Path | None = None) -> None:
    """
    Save the decrypted hex seed to a file (for persistence).

    By spec, inside Docker this must be /data/seed.txt.
    Here we use SEED_FILE_PATH and will point it to /data/seed.txt in Docker.
    """
    if path is None:
        path = SEED_FILE_PATH

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    validate_hex_seed(seed_hex)

    # Write as plain text with newline
    path.write_text(seed_hex + "\n")

    # Optional: adjust permissions (best effort, may be ignored on Windows)
    try:
        os.chmod(path, 0o600)  # readable/writable by owner only
    except PermissionError:
        # On some systems (e.g., Windows) this may fail; ignore
        pass
