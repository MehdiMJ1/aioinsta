from collections import defaultdict
from typing import Optional, Union, List, Tuple, Dict

from asyncpg import Record
from asyncpg.pool import PoolConnectionProxy
from sqlalchemy.sql import select, desc, func
from aiohttp import web

from api.db.schema import posts, users, likes, comments
from api.utils.exceptions import UserNotFoundException


QUERY_USERS_POSTS_LIMIT = 10
QUERY_FOLLOWERS_LIMIT = 1000


async def get_user_or_exception(
    conn: PoolConnectionProxy, *, user_id: int
) -> Optional[Record]:
    """
    Find post's object by id.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User ID
    :type user_id: int
    :raise UserNotFoundException: User not found
    :return: User's object
    :rtype: Union[Record, None]
    """

    user = await conn.fetchrow(
        select([
            users.c.id,
            users.c.username,
            users.c.name,
            users.c.description,
            users.c.email
        ])
        .where(users.c.id == user_id)
    )

    if user is None:
        raise UserNotFoundException()

    return user


async def create_user(
    conn, *, username, name, email, password, description=""
):
    """"""


async def edit_user(
    conn, *, user_id, username, name, email, password, description=""
):
    """"""


async def delete_user(conn, *, user_id):
    """"""


async def get_users_posts(conn, *, user_id, limit=QUERY_USERS_POSTS_LIMIT):
    """"""


async def get_users_posts_count(conn, *, user_id):
    """"""


async def get_users_followers(conn, *, user_id, limit=QUERY_FOLLOWERS_LIMIT):
    """"""


async def get_users_followers_count(conn, *, user_id):
    """"""


async def get_users_followees(conn, *, user_id, limit=QUERY_FOLLOWERS_LIMIT):
    """"""


async def get_users_followees_count(conn, *, user_id):
    """"""


async def follow_user(conn, *, user_id, follower_id):
    """"""


async def unfollow_user(conn, *, user_id, follower_id):
    """"""


async def is_follow_user(conn, *, user_id, follower_id):
    """"""


def hash_password(password):
    """"""


def check_password(password, hash_):
    """"""

    return hash_password(password=password) == hash_
