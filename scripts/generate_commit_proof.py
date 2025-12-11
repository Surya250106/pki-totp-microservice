#!/usr/bin/env python3
# scripts/generate_commit_proof.py
import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Paths (adjust if needed)
STUDENT_PRIV = Path("student_private.pem")
INSTRUCTOR_PUB = Path("instructor_public.pem")

def get_commit_hash() -> str:
    out = subprocess.check_output(["git", "log", "-1", "--format=%H"])
    return out.decode().strip()

def load_private_key(path: Path):
    pem = path.read_bytes()
    return serialization.load_pem_private_key(pem, password=None)

def load_public_key(path: Path):
    pem = path.read_bytes()
    return serialization.load_pem_public_key(pem)

def sign_message_ascii(message: str, private_key) -> bytes:
    # message must be ASCII bytes of commit hash
    data = message.encode("utf-8")
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext

def main():
    commit_hash = get_commit_hash()
    print("Commit Hash:", commit_hash)

    priv = load_private_key(STUDENT_PRIV)
    sig = sign_message_ascii(commit_hash, priv)

    pub = load_public_key(INSTRUCTOR_PUB)
    encrypted = encrypt_with_public_key(sig, pub)

    b64 = base64.b64encode(encrypted).decode("utf-8")
    print("Encrypted Commit Signature (BASE64):")
    print(b64)

if __name__ == "__main__":
    main()
