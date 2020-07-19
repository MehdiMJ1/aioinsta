import datetime
import pytest

from api.logic.posts import (get_posts, get_post_or_exception, edit_post_text,
                             create_post, delete_post, like_post, unlike_post,
                             get_posts_likes_count, get_posts_comments_count,
                             comment_post, delete_post_comment,
                             get_posts_comments)
from api.tests.setup import client, create_users, database
from api.utils.exceptions import PostNotFoundException, UserNotFoundException


async def test_post_creating(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        user_id = (await create_users(conn, 1))[0]

        with pytest.raises(UserNotFoundException):
            await create_post(conn, user_id=0, text="", image="")

        post_id = await create_post(
            conn, user_id=user_id, text="Test post", image="Base64 image"
        )

        assert isinstance(post_id, int)

        assert len(await get_posts(conn)) == 1

        post = await get_post_or_exception(conn, post_id=post_id)

        assert (post.get("id") == post_id and
                post.get("user_id") == user_id and
                post.get("text") == "Test post" and
                post.get("image") == "Base64 image" and
                isinstance(post.get("timestamp"), datetime.datetime))


async def test_post_getting(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        user_id = (await create_users(conn, 1))[0]

        assert await get_posts(conn) == []
        assert await get_posts(conn, limit=3) == []

        with pytest.raises(PostNotFoundException):
            await get_post_or_exception(conn, post_id=1)

        posts_ids = []

        for i in range(5):
            posts_ids.append(await create_post(
                conn, user_id=user_id, text=f"{i}", image=f"{i}"
            ))

        posts = [await get_post_or_exception(conn, post_id=post_id)
                 for post_id in posts_ids]

        posts.reverse()

        assert await get_posts(conn) == posts
        assert await get_posts(conn, limit=1) == posts[:1]
        assert await get_posts(conn, limit=3) == posts[:3]


async def test_post_editing(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:
        user_id = (await create_users(conn, 1))[0]
        post_id = await create_post(
            conn, user_id=user_id, text="Test post", image="Base64 image"
        )

        with pytest.raises(PostNotFoundException):
            await edit_post_text(conn, post_id=post_id+1, text="La")

        for text in ("Test text 2", "Ha-ha-ha", "<br><p>LA</p>", None):
            assert await edit_post_text(
                conn, post_id=post_id, text=text
            ) == post_id

            assert (
                await get_post_or_exception(conn, post_id=post_id)
            ).get("text") == text


async def test_post_deleting(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:
        user_id = (await create_users(conn, 1))[0]

        for i in range(7):
            post_id = await create_post(
                conn, user_id=user_id, text=f"{i}", image=f"{i}"
            )

            assert await delete_post(conn, post_id=post_id)

            with pytest.raises(PostNotFoundException):
                await delete_post(conn, post_id=post_id)


async def test_post_likes(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:
        with pytest.raises(PostNotFoundException):
            await like_post(conn, post_id=1, user_id=1)

        with pytest.raises(PostNotFoundException):
            await unlike_post(conn, post_id=1, user_id=1)

        with pytest.raises(PostNotFoundException):
            await get_posts_likes_count(conn, post_id=1)

        users = await create_users(conn, 3)
        posts = []

        for i in range(len(users), 0, -1):
            user_id = users[i - 1]

            for j in range(i):
                post_id = await create_post(
                    conn, user_id=user_id, text=f"Test", image=f"Test"
                )

                assert await get_posts_likes_count(conn, post_id=post_id) == 0

                with pytest.raises(UserNotFoundException):
                    await like_post(conn, post_id=post_id, user_id=4)

                with pytest.raises(UserNotFoundException):
                    await unlike_post(conn, post_id=post_id, user_id=4)

                assert await get_posts_likes_count(conn, post_id=post_id) == 0

                posts.append(post_id)

        for n, user in enumerate(users):
            for m, post in enumerate(posts):

                assert await like_post(conn, post_id=post, user_id=user)

                assert await get_posts_likes_count(
                    conn, post_id=post
                ) == n + 1

                assert not await like_post(conn, post_id=post, user_id=user)

                assert await get_posts_likes_count(
                    conn, post_id=post
                ) == n + 1

                assert await unlike_post(conn, post_id=post, user_id=user)

                assert await get_posts_likes_count(
                    conn, post_id=post
                ) == n

                assert not await unlike_post(conn, post_id=post, user_id=user)

                assert await get_posts_likes_count(
                    conn, post_id=post
                ) == n

                assert await like_post(conn, post_id=post, user_id=user)

                assert await get_posts_likes_count(
                    conn, post_id=post
                ) == n + 1


async def test_post_comments(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        with pytest.raises(PostNotFoundException):
            await get_posts_comments_count(conn, post_id=1)

        with pytest.raises(PostNotFoundException):
            await comment_post(conn, post_id=1, user_id=2, text="")

        assert not await delete_post_comment(conn, comment_id=1)

        user_id = (await create_users(conn, 1))[0]
        post_id = await create_post(
            conn, user_id=user_id, text=f"Test", image=f"Test"
        )

        with pytest.raises(UserNotFoundException):
            await comment_post(conn, post_id=post_id, user_id=2, text="")

        assert await get_posts_comments_count(conn, post_id=post_id) == 0

        comment_id = await comment_post(
            conn, post_id=post_id, user_id=user_id, text="Test comment"
        )

        assert isinstance(comment_id, int)

        assert await get_posts_comments_count(conn, post_id=post_id) == 1

        comment = (await get_posts_comments(conn, post_id=post_id))[0]

        assert (comment.get("user_id") == user_id and
                comment.get("text") == "Test comment" and
                isinstance(comment.get("timestamp"), datetime.datetime))

        assert await delete_post_comment(conn, comment_id=comment_id)

        assert await get_posts_comments_count(conn, post_id=post_id) == 0

        assert not await delete_post_comment(conn, comment_id=comment_id)

        assert await get_posts_comments_count(conn, post_id=post_id) == 0

        await comment_post(
            conn, post_id=post_id, user_id=user_id, text="Test comment 1"
        )

        await comment_post(
            conn, post_id=post_id, user_id=user_id, text="Test comment 2"
        )

        await comment_post(
            conn, post_id=post_id, user_id=user_id, text="Test comment 3"
        )

        assert await get_posts_comments_count(conn, post_id=post_id) == 3

        assert len(await get_posts_comments(conn, post_id=post_id)) == 3
