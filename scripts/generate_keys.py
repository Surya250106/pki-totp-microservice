from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair with public exponent 65537 and size 4096 bits.
    Saves:
      - student_private.pem
      - student_public.pem
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # Private key in PEM (PKCS8)
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Public key in PEM (SubjectPublicKeyInfo)
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open("student_private.pem", "wb") as f:
        f.write(priv_pem)

    with open("student_public.pem", "wb") as f:
        f.write(pub_pem)

    print("Generated student_private.pem and student_public.pem")

if __name__ == "__main__":
    generate_rsa_keypair()
