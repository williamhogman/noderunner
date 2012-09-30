import hashlib
import hmac


def sign_challenge(secret, challenge):
    """Signs a challenge with a secret.
    The challenge should be the ascii
    representation of a hexadecimal random number
    """
    return hmac.new(secret, challenge, hashlib.sha256).digest()
