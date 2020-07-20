import pytest
from typing import Any, Callable, List, Optional

from asyncpg.pool import PoolConnectionProxy

from api.__main__ import init_app
from api.config import TestConfig
from api.db import get_engine
from api.db.schema import metadata, users


config = TestConfig.load_config()
engine = get_engine(config)


@pytest.fixture
async def client(aiohttp_client: Callable) -> Any:
    """
    Fixture of application's instance.

    :param aiohttp_client: Wrapper of application
    :type aiohttp_client: Callable
    :return: Wrapped application instance
    :rtype: Any
    """

    app = await init_app(config)
    client = await aiohttp_client(app)

    return client


@pytest.fixture
def database() -> None:
    """Fixture for setup/teardown db and tables in it."""

    db_name = config.get("get_db_params").get("db")

    setup_db(db_name)
    create_tables()

    yield

    drop_tables()
    teardown_db(db_name)


def teardown_db(db_name: str) -> None:
    """
    Teardown database after tests.

    :param db_name: Database name
    :type db_name: str
    """

    with engine.connect() as conn:
        # terminate all connections to be able to drop database
        conn.execute(
            f"""
            SELECT 
                pg_terminate_backend(pg_stat_activity.pid)
            FROM 
                pg_stat_activity
            WHERE 
                pg_stat_activity.datname = '{db_name}' AND 
                pid <> pg_backend_pid();
        """
        )
        conn.execute(f"DROP DATABASE IF EXISTS {db_name}")


def setup_db(db_name: str) -> None:
    """Setup database before tests."""

    with engine.connect() as conn:
        # teardown database if it exists
        teardown_db(db_name)

        conn.execute(f"CREATE DATABASE {db_name}")


def create_tables() -> None:
    """Create all needed tables before test."""

    metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all tables after test."""

    metadata.drop_all(bind=engine)


async def create_users(
    conn: PoolConnectionProxy, count: int = 1
) -> List[Optional[int]]:
    """
    Create users and return ids

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param count: Count of users to create
    :type count: int
    :return: List of ids
    :rtype: List[Optional[int]]
    """

    values = [
        (
            "('Test user {i}', 'Test user {i}', 'Test user {i}', "
            "'test-user-{i}@test.test', '')"
        ).replace("{i}", str(i))
        for i in range(1, count + 1)
    ]

    result = await conn.fetch(
        f"""
        INSERT INTO 
            "user" (username, name, description, email, password_hash) 
        VALUES 
            {", ".join(values)} 
        RETURNING id
        """
    )

    return list(map(lambda record: record.get("id"), result))
