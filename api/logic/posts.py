from typing import List, Optional

from asyncpg import Record
from asyncpg.pool import PoolConnectionProxy
from sqlalchemy.sql import and_, desc, func, select

from api.db.schema import comments, likes, posts, users
from api.logic.users import get_user_or_exception
from api.utils.exceptions import PostNotFoundException


QUERY_POSTS_LIMIT: int = 10


async def get_posts(
    conn: PoolConnectionProxy, *, limit: int = QUERY_POSTS_LIMIT
) -> List[Optional[Record]]:
    """
    Get list of post's objects.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param limit: Limit of the list
    :type limit: int
    :return: List of post's objects
    :rtype: List[Optional[Record]]
    """

    join = posts.join(users, posts.c.user_id == users.c.id)
    records = await conn.fetch(
        select([posts, users.c.username])
        .select_from(join)
        .order_by(desc(posts.c.timestamp))
        .limit(limit)
    )

    return records


async def get_post_or_exception(
    conn: PoolConnectionProxy, *, post_id: int
) -> Optional[Record]:
    """
    Find post's object by id.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post ID
    :type post_id: int
    :raise PostNotFoundException: Post not found
    :return: Post's object
    :rtype: Optional[Record]
    """

    join = posts.join(users, posts.c.user_id == users.c.id)
    post = await conn.fetchrow(
        select([posts, users.c.username])
        .select_from(join)
        .where(posts.c.id == post_id)
    )

    if post is None:
        raise PostNotFoundException()

    return post


async def create_post(
    conn: PoolConnectionProxy, *, user_id: int, text: str, image: str
) -> int:
    """
    Create a new post.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param user_id: Post's owner
    :type user_id: int
    :param text: Post's text
    :type text: str
    :param image: Base64 string of post's image
    :type image: str
    :raise UserNotFoundException: User not found
    :return: Post's id
    :rtype: int
    """

    await get_user_or_exception(conn, user_id=user_id)

    post_id = await conn.fetchval(
        """
        INSERT INTO 
            post (user_id, text, image, timestamp) 
        VALUES 
            ($1, $2, $3, NOW()) 
        RETURNING id
        """,
        user_id,
        text,
        image,
    )

    return post_id


async def edit_post_text(
    conn: PoolConnectionProxy, *, post_id: int, text: str,
) -> int:
    """
    Edit the post's text.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :param text: Post's text
    :type text: str
    :raise PostNotFoundException: Post not found
    :return: Post's id
    :rtype: int
    """

    await get_post_or_exception(conn, post_id=post_id)

    await conn.execute(
        """
        UPDATE 
            post 
        SET 
            text = $1
        WHERE
            id = $2 
        """,
        text,
        post_id,
    )

    return post_id


async def delete_post(
    conn: PoolConnectionProxy, *, post_id: int
) -> bool:
    """
    Delete the post.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :raise PostNotFoundException: Post not found
    :return: Result of operation
    :rtype: bool
    """

    await get_post_or_exception(conn, post_id=post_id)

    result = await conn.fetchval(
        """
        DELETE FROM 
            post 
        WHERE
            id = $1
        RETURNING id
        """,
        post_id,
    )

    return True if result is not None else False


async def get_posts_likes_count(
    conn: PoolConnectionProxy, *, post_id: int
) -> int:
    """
    Get count of post's likes.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :raise PostNotFoundException: Post not found
    :return: Count of likes
    :rtype: int
    """

    await get_post_or_exception(conn, post_id=post_id)

    result = await conn.fetchval(
        select([func.count()]).where(likes.c.post_id == post_id)
    )

    return result


async def get_posts_comments_count(
    conn: PoolConnectionProxy, *, post_id: int
) -> int:
    """
    Get count of post's comments.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :raise PostNotFoundException: Post not found
    :return: Count of comments
    :rtype: int
    """

    await get_post_or_exception(conn, post_id=post_id)

    result = await conn.fetchval(
        select([func.count()]).where(comments.c.post_id == post_id)
    )

    return result


async def get_posts_comments(
    conn: PoolConnectionProxy, *, post_id: int
) -> List[Optional[Record]]:
    """
    Get all post's comments.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :raise PostNotFoundException: Post not found
    :return: Post's comments
    :rtype: List[Optional[Record]]
    """

    await get_post_or_exception(conn, post_id=post_id)

    result = await conn.fetch(
        select([
            comments.c.user_id, comments.c.text, comments.c.timestamp]
        )
        .where(comments.c.post_id == post_id)
        .order_by(comments.c.timestamp)
    )

    return result


async def is_post_liked(
    conn: PoolConnectionProxy, *, post_id: int, user_id: int
) -> bool:
    """
    Check is post liked by user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :raise PostNotFoundException: Post not found
    :return: Is post liked by user
    :rtype: bool
    """

    await get_post_or_exception(conn, post_id=post_id)
    await get_user_or_exception(conn, user_id=user_id)

    result = await conn.fetchval(
        select([func.count()]).where(and_(
            likes.c.post_id == post_id,
            likes.c.user_id == user_id
        ))
    )

    return bool(result)


async def like_post(
    conn: PoolConnectionProxy, *, post_id: int, user_id: int
) -> bool:
    """
    Like post by user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :raise PostNotFoundException: Post not found
    :return: Result of operation
    :rtype: bool
    """

    if await is_post_liked(conn, post_id=post_id, user_id=user_id):
        return False

    await conn.execute(
        likes.insert().values(
            post_id=post_id, user_id=user_id
        )
    )

    return True


async def unlike_post(
    conn: PoolConnectionProxy, *, post_id: int, user_id: int
) -> bool:
    """
    Unlike post by user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :param user_id: User's identifier
    :type user_id: int
    :raise UserNotFoundException: User not found
    :raise PostNotFoundException: Post not found
    :return: Result of operation
    :rtype: bool
    """

    if not await is_post_liked(conn, post_id=post_id, user_id=user_id):
        return False

    await conn.execute(
        likes.delete().where(and_(
            likes.c.post_id == post_id,
            likes.c.user_id == user_id
        ))
    )

    return True


async def comment_post(
    conn: PoolConnectionProxy, *, post_id: int, user_id: int, text: str
) -> int:
    """
    Comment post by user.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param post_id: Post's identifier
    :type post_id: int
    :param user_id: User's identifier
    :type user_id: int
    :param text: Comment's text
    :type text: str
    :raise UserNotFoundException: User not found
    :raise PostNotFoundException: Post not found
    :return: Comment's id
    :rtype: int
    """

    await get_post_or_exception(conn, post_id=post_id)
    await get_user_or_exception(conn, user_id=user_id)

    comment_id = await conn.fetchval(
        """
        INSERT INTO 
            comment (post_id, user_id, text, timestamp) 
        VALUES 
            ($1, $2, $3, NOW()) 
        RETURNING id
        """,
        post_id,
        user_id,
        text,
    )

    return comment_id


async def delete_post_comment(
    conn: PoolConnectionProxy, *, comment_id: int
) -> bool:
    """
    Delete post's comment.

    :param conn: Pool of connections to database
    :type conn: PoolConnectionProxy
    :param comment_id: Comment's identifier
    :type comment_id: int
    :return: Result of operation
    :rtype: bool
    """

    result = await conn.fetchval(
        """
        DELETE FROM 
            comment 
        WHERE
            id = $1
        RETURNING id
        """,
        comment_id,
    )

    return True if result is not None else False
