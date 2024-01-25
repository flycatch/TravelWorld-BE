from django.conf import settings
from hashids import Hashids


def encode(value):
    """
    Function to  hash hid the int value.

    Input Params:
        value(int): int value
    Returns:
        hashed string.
    """
    hasher = Hashids(min_length=settings.HASHID_MIN_LENGTH, salt=settings.HASHHID_SALT)
    try:
        value = int(value)
        return hasher.encode(value)
    except:
        return None


def decode(value):
    """
    Function to  decode hash hid value.

    Input Params:
        value(str): str value
    Returns:
        int value.
    """
    hasher = Hashids(min_length=settings.HASHID_MIN_LENGTH, salt=settings.HASHHID_SALT)
    try:
        return hasher.decode(value)[0]
    except:
        return None