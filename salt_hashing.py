import hashlib
import os

def generate_salt(length: int = 16) -> bytes:
    # generates cryptographically secure salt, urandom makes sure each result is truly unique
    return os.urandom(length)


def hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:

    # if no salt is provided generate one
    if salt is None:
        salt = generate_salt()

    # its important to encode plaintext to bytes before hashing
    password_bytes = password.encode("utf-8")

    # add salt to password
    combined = salt + password_bytes

    # hash salt+password with SHA512
    hash_bytes = hashlib.sha512(combined).digest()

    return salt, hash_bytes
