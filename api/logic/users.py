from typing import List, Optional

from asyncpg import Record
from asyncpg.pool import PoolConnectionProxy
from sqlalchemy.sql import and_, desc, func, select

from api.db.schema import followers, posts, users
from api.utils.exceptions import UserNotFoundException
from api.utils.hashing import hash_string


QUERY_USERS_LIMIT: int = 10
QUERY_USERS_POSTS_LIMIT = 10
QUERY_FOLLOWERS_LIMIT = 1000


async def get_users(
    conn: PoolConnectionProxy, *, limit: int = QUERY_USERS_LIMIT
) -> List[Optional[Record]]:
    """
    Get list of user's objects.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param limit: Limit of the list
    :type limit: int
    :return: List of user's objects
    :rtype: List[Optional[Record]]
    """

    records = await conn.fetch(
        select([
            users.c.id,
            users.c.username,
            users.c.name,
            users.c.description,
            users.c.email
        ])
        .limit(limit)
    )

    return records


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
    :rtype: Optional[Record]
    """

    user = await conn.fetchrow(
        select(
            [
                users.c.id,
                users.c.username,
                users.c.name,
                users.c.description,
                users.c.email,
            ]
        ).where(users.c.id == user_id)
    )

    if user is None:
        raise UserNotFoundException()

    return user


async def create_user(
    conn: PoolConnectionProxy,
    *,
    username: str,
    name: str,
    email: str,
    password: str,
    description: str = ""
) -> int:
    """
    Create a new user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param username: User's username
    :type username: str
    :param name: User's real name
    :type name: str
    :param email: User's email
    :type email: str
    :param password: User's password
    :type password: str
    :param description: Description about user's profile
    :type description: str
    :return: User's id
    :rtype: int
    """

    password = hash_password(password=password)

    user_id = await conn.fetchval(
        """
        INSERT INTO 
            "user" (username, name, email, password_hash, description) 
        VALUES 
            ($1, $2, $3, $4, $5) 
        RETURNING id
        """,
        username,
        name,
        email,
        password,
        description,
    )

    return user_id


async def delete_user(conn: PoolConnectionProxy, *, user_id: int):
    """
    Delete the user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :return: Result of operation
    :rtype: bool
    """

    await get_user_or_exception(conn, user_id=user_id)

    result = await conn.fetchval(
        """
        DELETE FROM 
            "user" 
        WHERE
            id = $1
        RETURNING id
        """,
        user_id,
    )

    return True if result is not None else False


async def get_users_posts(
    conn: PoolConnectionProxy,
    *,
    user_id: int,
    limit: int = QUERY_USERS_POSTS_LIMIT
) -> List[Optional[Record]]:
    """
    Get list of user's post objects.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :param limit: Limit of the list
    :type limit: int
    :raise UserNotFoundException: User not found
    :return: List of post's objects
    :rtype: List[Optional[Record]]
    """

    await get_user_or_exception(conn, user_id=user_id)

    join = posts.join(users, posts.c.user_id == users.c.id)
    records = await conn.fetch(
        select([posts, users.c.username])
        .select_from(join)
        .where(posts.c.user_id == user_id)
        .order_by(desc(posts.c.timestamp))
        .limit(limit)
    )

    return records


async def get_users_posts_count(
    conn: PoolConnectionProxy, *, user_id: int
) -> int:
    """
    Get count of user's posts.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :return: Count of user's posts
    :rtype: int
    """

    await get_user_or_exception(conn, user_id=user_id)

    count = await conn.fetchval(
        select([func.count()]).where(posts.c.user_id == user_id)
    )

    return count


async def get_users_followers(
    conn: PoolConnectionProxy,
    *,
    user_id: int,
    limit: int = QUERY_FOLLOWERS_LIMIT
) -> List[Optional[int]]:
    """
    Get list of user's followers.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :param limit: Limit of the list
    :type limit: int
    :raise UserNotFoundException: User not found
    :return: List of followers's id
    :rtype: List[Optional[int]]
    """

    await get_user_or_exception(conn, user_id=user_id)

    records = await conn.fetch(
        select([followers.c.from_user])
        .where(followers.c.to_user == user_id)
        .limit(limit)
    )

    return list(map(lambda record: record.get("from_user"), records))


async def get_users_followers_count(
    conn: PoolConnectionProxy, *, user_id: int
) -> int:
    """
    Get count of user's followers.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :return: Count of followers
    :rtype: int
    """

    await get_user_or_exception(conn, user_id=user_id)

    count = await conn.fetchval(
        select([func.count()]).where(followers.c.to_user == user_id)
    )

    return count


async def get_users_followees(
    conn: PoolConnectionProxy,
    *,
    user_id: int,
    limit: int = QUERY_FOLLOWERS_LIMIT
) -> List[Optional[int]]:
    """
    Get list of user's followees.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :param limit: Limit of the list
    :type limit: int
    :raise UserNotFoundException: User not found
    :return: List of followees's id
    :rtype: List[Optional[int]]
    """

    await get_user_or_exception(conn, user_id=user_id)

    records = await conn.fetch(
        select([followers.c.to_user])
        .where(followers.c.from_user == user_id)
        .limit(limit)
    )

    return list(map(lambda record: record.get("to_user"), records))


async def get_users_followees_count(
    conn: PoolConnectionProxy, *, user_id: int
) -> int:
    """
    Get count of user's followees.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :return: Count of followees
    :rtype: int
    """

    await get_user_or_exception(conn, user_id=user_id)

    count = await conn.fetchval(
        select([func.count()]).where(followers.c.from_user == user_id)
    )

    return count


async def follow_user(
    conn: PoolConnectionProxy, *, user_id: int, follower_id: int
) -> bool:
    """
    Follow the user by another user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User who follow
    :type user_id: int
    :param follower_id: User whom follow
    :type follower_id: int
    :raise UserNotFoundException: User not found
    :return: Result of operation
    :rtype: bool
    """

    if await is_follow_user(conn, user_id=user_id, follower_id=follower_id):
        return False

    await conn.execute(
        followers.insert().values(from_user=user_id, to_user=follower_id)
    )

    return True


async def unfollow_user(
    conn: PoolConnectionProxy, *, user_id: int, follower_id: int
) -> bool:
    """
    Unfollow the user from another user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User who unfollow
    :type user_id: int
    :param follower_id: User whom unfollow
    :type follower_id: int
    :raise UserNotFoundException: User not found
    :return: Result of operation
    :rtype: bool
    """

    if not await is_follow_user(
        conn, user_id=user_id, follower_id=follower_id
    ):
        return False

    await conn.execute(
        followers.delete().where(
            and_(
                followers.c.from_user == user_id,
                followers.c.to_user == follower_id,
            )
        )
    )

    return True


async def is_follow_user(
    conn: PoolConnectionProxy, *, user_id: int, follower_id: int
) -> bool:
    """
    Check is post liked by user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: User who follow
    :type user_id: int
    :param follower_id: User whom follow
    :type follower_id: int
    :raise UserNotFoundException: User not found
    :return: Is user followed by another user
    :rtype: bool
    """

    await get_user_or_exception(conn, user_id=user_id)
    await get_user_or_exception(conn, user_id=follower_id)

    result = await conn.fetchval(
        select([func.count()]).where(
            and_(
                followers.c.from_user == user_id,
                followers.c.to_user == follower_id,
            )
        )
    )

    return bool(result)


def hash_password(password: str) -> str:
    """
    Hash user's password.

    :param password: User's password
    :type password: str
    :return: Salt and hash of password
    :rtype: str
    """

    return hash_string(password)


def check_password(password: str, hash_: str) -> bool:
    """
    Check is user's password correct.

    :param password: Password to check
    :type password: str
    :param hash_: Salt and hash of user's password
    :type hash_: str
    :return: Result of comparison
    :rtype: bool
    """

    salt = hash_[:64]  # Getting salt from password's hash
    hashed_password = hash_string(password, salt=salt.encode("ascii"))

    return hash_ == hashed_password
