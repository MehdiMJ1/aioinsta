import pytest

from api.logic.posts import create_post, get_post_or_exception
from api.logic.users import (
    create_user,
    get_user_or_exception,
    get_users,
    delete_user,
    get_users_posts,
    get_users_posts_count,
    get_users_followers,
    get_users_followers_count,
    get_users_followees,
    get_users_followees_count,
    follow_user,
    unfollow_user,
    hash_password,
    check_password
)
from api.tests.setup import client, database
from api.utils.exceptions import UserNotFoundException


async def test_user_creating(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        user_id = await create_user(
            conn,
            username="Test username",
            name="Test name",
            email="test@user.email",
            password="Test password",
            description="Test description"
        )

        assert isinstance(user_id, int)

        user = await get_user_or_exception(conn, user_id=user_id)

        assert (
            user.get("id") == user_id
            and user.get("username") == "Test username"
            and user.get("name") == "Test name"
            and user.get("email") == "test@user.email"
            and user.get("description") == "Test description"
        )


async def test_user_getting(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        with pytest.raises(UserNotFoundException):
            await get_user_or_exception(conn, user_id=1)

        users_ids = []

        for i in range(5):
            users_ids.append(
                await create_user(
                    conn,
                    username=f"Test username {i}",
                    name=f"Test name {i}",
                    email=f"test-{i}@user.email",
                    password=f"Test password {i}",
                    description=f"Test description {i}"
                )
            )

        users = [
            await get_user_or_exception(conn, user_id=user_id)
            for user_id in users_ids
        ]

        assert await get_users(conn) == users
        assert await get_users(conn, limit=1) == users[:1]
        assert await get_users(conn, limit=3) == users[:3]


async def test_user_deleting(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        for i in range(7):
            user_id = await create_user(
                conn,
                username=f"Test username {i}",
                name="fTest name {i}",
                email=f"test-{i}@user.email",
                password=f"Test password {i}",
                description=f"Test description {i}"
            )

            assert await delete_user(conn, user_id=user_id)

            with pytest.raises(UserNotFoundException):
                await delete_user(conn, user_id=user_id)


async def test_get_users_posts(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        with pytest.raises(UserNotFoundException):
            await get_users_posts(conn, user_id=1)

        user_id = await create_user(
            conn,
            username="Test username",
            name="Test name",
            email="test@user.email",
            password="Test password",
            description="Test description"
        )

        posts = []

        for i in range(10):
            post_id = await create_post(
                conn, user_id=user_id, text=f"text {i}", image=f"image {i}"
            )
            posts.append(await get_post_or_exception(conn, post_id=post_id))
            assert await get_users_posts_count(
                conn, user_id=user_id
            ) == len(posts)

        posts.reverse()

        assert await get_users_posts(conn, user_id=user_id) == posts


async def test_user_following(client, database) -> None:
    """"""

    async with client.server.app["db"] as conn:

        with pytest.raises(UserNotFoundException):
            await follow_user(conn, user_id=1, follower_id=2)

        with pytest.raises(UserNotFoundException):
            await unfollow_user(conn, user_id=1, follower_id=2)

        with pytest.raises(UserNotFoundException):
            await get_users_followers(conn, user_id=1)

        with pytest.raises(UserNotFoundException):
            await get_users_followers_count(conn, user_id=1)

        with pytest.raises(UserNotFoundException):
            await get_users_followees(conn, user_id=1)

        with pytest.raises(UserNotFoundException):
            await get_users_followees_count(conn, user_id=1)

        users = []

        for i in range(6):
            users.append(await create_user(
                conn,
                username=f"Test username {i}",
                name=f"Test name {i}",
                email=f"test-{i}@user.email",
                password=f"Test password {i}",
                description=f"Test description {i}"
            ))

            assert await get_users_followers(conn, user_id=users[i]) == []
            assert await get_users_followees(conn, user_id=users[i]) == []
            assert await get_users_followers_count(conn, user_id=users[i]) == 0
            assert await get_users_followees_count(conn, user_id=users[i]) == 0

            for j in range(i + 1):
                assert await follow_user(
                    conn, user_id=users[j], follower_id=users[i]
                )
                assert not await follow_user(
                    conn, user_id=users[j], follower_id=users[i]
                )
                assert await get_users_followers(
                    conn, user_id=users[i]
                ) == list(range(1, j + 2))
                assert await get_users_followers_count(
                    conn, user_id=users[i]
                ) == j + 1
                assert await get_users_followees(
                    conn, user_id=users[j]
                ) == list(range(j + 1, i + 2))
                assert await get_users_followees_count(
                    conn, user_id=users[j]
                ) == (i + 2) - (j + 1)
                assert await unfollow_user(
                    conn, user_id=users[j], follower_id=users[i]
                )
                assert not await unfollow_user(
                    conn, user_id=users[j], follower_id=users[i]
                )
                assert await get_users_followers(
                    conn, user_id=users[i]
                ) == list(range(1, j + 1))
                assert await get_users_followers_count(
                    conn, user_id=users[i]
                ) == j
                assert await get_users_followees(
                    conn, user_id=users[j]
                ) == list(range(j + 1, i + 1))
                assert await get_users_followees_count(
                    conn, user_id=users[j]
                ) == (i + 1) - (j + 1)
                assert await follow_user(
                    conn, user_id=users[j], follower_id=users[i]
                )


async def test_user_password() -> None:
    """"""

    for password in ("Test", "BAD*YIASGf7vDG(Vgs(", "", "123"):
        hashed_password = hash_password(password)

        assert check_password(password, hashed_password)
        assert hashed_password != password
