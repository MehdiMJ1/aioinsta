import datetime
import json
from typing import Any

from asyncpg import Record


def to_json(data: Any) -> str:
    """
    Decorator over usual json.dumps function with specific parameters.

    :param data: Data to serialize in json format
    :param data: Any
    :return: Json string
    :rtype: str
    """

    return json.dumps(data, indent=4, default=perfect_json_serializer)


def perfect_json_serializer(value: Any) -> Any:
    """
    Make some types of objects serializable to json.

    :param value: Value to transform
    :type value: Any
    :return: Json serializable object
    :rtype: Any
    """

    if isinstance(value, datetime.datetime):
        return value.__str__()
    elif isinstance(value, Record):
        return dict(value)
