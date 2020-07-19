from typing import Union, Any

import aiosqlite
from aiosqlite import Connection
import asyncpgsa
from asyncpg.pool import Pool
from sqlalchemy import create_engine


NAMING_CONVECTION = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


async def init_db(config: dict) -> Union[Pool, Connection]:
    """
    Initiate db connection.

    :param config: Application configuration
    :type config: dict
    :return: Pool of db connection
    :rtype: Union[Pool, Connection]
    """

    db_url = config["db_url"]

    if db_url.startswith("postgresql"):
        return await asyncpgsa.create_pool(dsn=db_url)

    return aiosqlite.connect(db_url)


def get_engine(config: dict) -> Any:
    """
    Get SQLAlchemy database engine.

    :param config: Application configuration
    :type config: dict
    :return: Database engine
    :rtype: Any
    """

    db_url = config["db_url"]

    return create_engine(db_url, isolation_level="AUTOCOMMIT")
