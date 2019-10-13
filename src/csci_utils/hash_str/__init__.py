from typing import AnyStr
from hashlib import sha256
import os


def get_csci_salt() -> bytes:
    """Returns the appropriate salt for CSCI E-29"""
    # retrieve os environment variable called CSCI_SALT
    SALT = os.environ["CSCI_SALT"]

    # convert hexadecimal salt to bytes equivalent and return those bytes
    return bytes.fromhex(SALT)


def hash_str(some_val: AnyStr, salt: AnyStr = ""):
    """Converts strings to hash digest

    :param some_val: thing to hash
    :param salt: Add randomness to the hashing
    :return: hash digest of input
    """
    # create a SHA-256 hash object
    h = sha256()

    # lambda function used to ensure input vars to the hash object are bytes
    encode = lambda x: x.encode() if isinstance(x, str) else x

    # feed hash object with salt bytes
    h.update(encode(salt))

    # feed hash object with bytes representation of the input string
    h.update(encode(some_val))

    # return digest of the data fed into the hash object
    return h.digest()


def get_user_id(username: str) -> str:
    """Converts username string to hash digest

    :param username: string to hash
    :return: first 8 chars in hex format of hash digest of input
    """
    # retrieve salt from environment variables
    salt = get_csci_salt()
    # compute and return hash digest of input
    return hash_str(username.lower(), salt=salt).hex()[:8]
