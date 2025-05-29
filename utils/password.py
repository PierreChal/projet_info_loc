import bcrypt

def hash_password_bcrypt(password: str, cost: int = 12) -> bytes:
    # cost détermine 2^cost : le nombre d’itérations
    salt = bcrypt.gensalt(rounds=cost)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password_bcrypt(hashed: bytes, password_attempt: str) -> bool:
    return bcrypt.checkpw(password_attempt.encode('utf-8'), hashed)
