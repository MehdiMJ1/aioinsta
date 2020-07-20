import binascii
import hashlib
import os
from typing import Optional


BYTES_COUNT: int = 60
SHA_ITER_COUNT: int = 100000
HASH_FUNC: str = "sha512"


def get_random_bytes(count: int = BYTES_COUNT) -> bytes:
    """
    Return count of random bytes.

    :param count: Count of bytes
    :type count: int
    :return: Random bytes
    :rtype: bytes
    """

    return os.urandom(count)


def generate_salt(random_bytes: Optional[bytes] = None) -> bytes:
    """
    Generate hash salt.

    :param random_bytes: Random bytes for salting
    :type random_bytes: Optional[bytes]
    :return: Salted bytes
    :rtype: bytes
    """

    random_bytes = get_random_bytes() if random_bytes is None else random_bytes

    return hashlib.sha256(random_bytes).hexdigest().encode("ascii")


def hash_string(
    string: str,
    *,
    salt: Optional[bytes] = None,
    sha_iter_count: int = SHA_ITER_COUNT,
    hash_func: str = HASH_FUNC
) -> str:
    """
    Hash string by input parameters.

    :param string: String to be hashed
    :type string: str
    :param salt: Salt for hashing
    :type salt: Optional[bytes]
    :param sha_iter_count: Count of hashing iterations
    :type sha_iter_count: int
    :param hash_func: Function for hashing
    :type hash_func: str
    :return: Hashed string
    :rtype: str
    """

    salt = generate_salt() if salt is None else salt

    hashed_string = hashlib.pbkdf2_hmac(
        hash_func, string.encode("utf-8"), salt, sha_iter_count
    )
    hashed_string = binascii.hexlify(hashed_string)

    return (salt + hashed_string).decode("ascii")
