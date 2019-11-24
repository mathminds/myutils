from typing import AnyStr
from hashlib import sha256
from functools import wraps
import os


def get_bytearray(value: AnyStr):
    """
    If value is a string type convert to bytes otherwise return value (which should be bytes)
    :param value:
    :return: value as bytes
    """
    if type(value) == str:
        return bytearray(value.encode())
    else:
        return bytearray(value)


def byte_params(func):
    """
    Decorator which will convert parameters to bytes before calling function
    :param func:
    :return: function wrapper with param converstion to bytes
    """

    @wraps(func)
    def function_wrapper(some_val: AnyStr, salt: AnyStr = ""):
        """ convert parameters to bytes """
        if not some_val:
            raise ValueError("No string provided to hash")
        if not salt:
            raise ValueError("No salt provided for hash")
        return func(get_bytearray(some_val), get_bytearray(salt))

    return function_wrapper


def get_csci_salt() -> bytes:
    """Returns the appropriate salt for CSCI E-29"""

    salt = os.getenv("CSCI_SALT")

    if not salt:
        return None
    else:
        return bytes.fromhex(salt)


@byte_params
def hash_str(some_val: AnyStr, salt: AnyStr = ""):
    """Converts strings to hash digest

    See: https://en.wikipedia.org/wiki/Salt_(cryptography)

    :param some_val: thing to hash
    :param salt: Add randomness to the hashing

    """
    encoded_val = salt + some_val
    # Compute hash value and return
    return sha256(encoded_val).digest()


def get_user_id(username: str) -> str:
    """
    Return the username as a hashed id value
    :param username:
    :return: hash user id
    """
    return get_user_hash(username.lower()).hex()[:8]


def get_user_hash(username, salt=None):
    """
     Returns the full hashed value for a given username
    :param username:
    :param salt:
    :return:
    """
    salt = salt or get_csci_salt()
    return hash_str(username, salt=salt)
