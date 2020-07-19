from aiohttp import web

from api.views import hello, PostList, Post, User


def setup_routes(app: web.Application) -> None:
    """
    Setup application routes.

    :param app: Current application
    :type app: web.Application
    """

    router = app.router

    router.add_get("/", hello, name="hello_world")

    router.add_view("/posts", PostList)
    router.add_view("/posts/{post_id:\d+}", Post)
    router.add_get("/posts/{post_id:\d+}/likes_count", Post.likes_count)
    router.add_get("/posts/{post_id:\d+}/comments_count", Post.comments_count)
    router.add_get("/posts/{post_id:\d+}/comments", Post.comments)

    router.add_view("/users/{user_id:\d+}", User)
