import datetime
import json
import pytest

from api.utils.hashing import hash_string, generate_salt, get_random_bytes
from api.utils.json_serializers import to_json


def test_random_bytes_getting():
    """"""

    for length in (5, 10, 50, 100, 1000):
        assert len(get_random_bytes(length)) == length

    for count in range(2, 1000):
        random_set = set([get_random_bytes() for _ in range(count)])

        assert len(random_set) == count


def test_salt_generating():
    """"""

    random_bytes = b"cbiyGAS&Cg97"

    assert generate_salt(random_bytes) == generate_salt(random_bytes)

    for _ in range(1000):
        assert generate_salt() != generate_salt()


def test_string_hashing():
    """"""

    count = 100

    hash_set = set([hash_string("Test string") for _ in range(count)])

    assert len(hash_set) == count

    assert hash_string("Test me") != hash_string("Test me", salt=b"Test salt")

    assert (hash_string("Another test", salt=b"sABIYFGA^S*F&GA") ==
            hash_string("Another test", salt=b"sABIYFGA^S*F&GA"))

    assert hash_string(
        "Another test", salt=b"sABIYFGA^S*F&GA", sha_iter_count=1000
    ) != hash_string(
        "Another test", salt=b"sABIYFGA^S*F&GA", sha_iter_count=999
    )

    assert hash_string(
        "Another test", salt=b"sABIYFGA^S*F&GA", hash_func="sha512"
    ) != hash_string(
        "Another test", salt=b"sABIYFGA^S*F&GA", hash_func="sha256"
    )

    hashed_string = hash_string("My lil test")

    assert hashed_string == hash_string(
        "My lil test", salt=(hashed_string[:64]).encode("ascii")
    )


def test_json_serializing():
    """"""

    date = datetime.datetime.now()

    with pytest.raises(TypeError):
        json.dumps(date)

    assert json.loads(to_json(date)) == str(date)

    for example in (
        1,
        1.0,
        True,
        None,
        False,
        "d",
        "<div>",
        [1, 2, 3, {1: 2}],
        {2: "3", "4": True},
        (1, 2, 3)
    ):
        assert json.dumps(example, indent=4) == to_json(example)
