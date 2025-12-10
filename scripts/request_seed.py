import json
import requests
from pathlib import Path

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# TODO: REPLACE THESE WITH YOUR REAL VALUES
STUDENT_ID = "23MH1A05G7"
GITHUB_REPO_URL = "https://github.com/Surya250106/pki-totp-microservice"


def request_seed(student_id: str, github_repo_url: str, api_url: str = API_URL):
    """
    Request encrypted seed from instructor API and save to encrypted_seed.txt
    """
    # 1. Read student public key from PEM file (keep the BEGIN/END markers)
    pub_path = Path("student_public.pem")
    if not pub_path.exists():
        raise FileNotFoundError("student_public.pem not found in repo root")

    public_key_pem = pub_path.read_text()

    # 2. Prepare JSON payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }

    # 3. Send POST request
    print("Sending request to instructor API...")
    resp = requests.post(
        api_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=20,
    )
    resp.raise_for_status()

    data = resp.json()
    if data.get("status") != "success" or "encrypted_seed" not in data:
        raise RuntimeError(f"API error or unexpected response: {data}")

    encrypted_seed = data["encrypted_seed"]

    # 4. Save encrypted seed to file (single line)
    out_path = Path("encrypted_seed.txt")
    out_path.write_text(encrypted_seed.strip() + "\n")

    print("Encrypted seed saved to encrypted_seed.txt")


if __name__ == "__main__":
    if "YOUR_STUDENT_ID_HERE" in STUDENT_ID:
        raise ValueError("Please edit request_seed.py and set STUDENT_ID to your real ID!")
    request_seed(STUDENT_ID, GITHUB_REPO_URL)
