from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .crypto_utils import (
    load_private_key,
    decrypt_seed,
    save_seed_to_file,
    SEED_FILE_PATH,
)
from .totp_utils import (
    generate_totp_code,
    verify_totp_code,
    get_seconds_remaining,
)

app = FastAPI(title="PKI + TOTP 2FA Microservice")


# ---------- Request/Response Models ----------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- Endpoint 1: POST /decrypt-seed ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    """
    Accept base64-encoded encrypted seed, decrypt using student private key,
    store persistently, and return {"status": "ok"} on success.

    On failure: return {"error": "Decryption failed"} with HTTP 500.
    """
    encrypted_seed_b64 = payload.encrypted_seed

    try:
        private_key = load_private_key("student_private.pem")
        hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
        # Save to persistent seed file
        save_seed_to_file(hex_seed, SEED_FILE_PATH)
    except Exception as e:
        # For debugging you might log e somewhere, but don't expose details to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )

    return {"status": "ok"}


# ---------- Endpoint 2: GET /generate-2fa ----------

@app.get("/generate-2fa")
def generate_2fa_endpoint():
    """
    Read seed from persistent storage, generate current TOTP code,
    calculate remaining validity seconds, and return:

        {"code": "123456", "valid_for": 30}

    On error (no seed): 500 + {"error": "Seed not decrypted yet"}
    """
    seed_path: Path = SEED_FILE_PATH
    if not seed_path.exists():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = seed_path.read_text().strip()
        code = generate_totp_code(hex_seed)
        valid_for = get_seconds_remaining(period=30)
    except Exception:
        # Any failure in reading/generating should be treated as 500
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    return {
        "code": code,
        "valid_for": valid_for,
    }


# ---------- Endpoint 3: POST /verify-2fa ----------

@app.post("/verify-2fa")
def verify_2fa_endpoint(payload: Verify2FARequest):
    """
    Accept {"code": "123456"}, verify against stored seed with ±1 period tolerance.

    Responses:
      - 200: {"valid": true/false}
      - 400: {"error": "Missing code"}
      - 500: {"error": "Seed not decrypted yet"}
    """
    code = payload.code

    # 1. Validate code presence
    if not code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Missing code"},
        )

    # 2. Ensure seed exists
    seed_path: Path = SEED_FILE_PATH
    if not seed_path.exists():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = seed_path.read_text().strip()
        is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    except Exception:
        # If something goes wrong reading or verifying, treat like missing seed
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    return {"valid": is_valid}
