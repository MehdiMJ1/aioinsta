from aiohttp import web

from api.logic.posts import (
    get_post_or_exception,
    get_posts,
    create_post,
    delete_post,
    get_posts_likes_count,
    get_posts_comments_count,
    get_posts_comments,
    PostNotFoundException,
)
from api.utils.exceptions import RecordNotFoundException
from api.utils.json_serializers import to_json
from api.views.base import BaseListWebView, BaseWebView


class PostList(web.View):
    """"""

    async def get(self):
        async with self.request.app["db"].acquire() as conn:
            posts = await get_posts(conn)

        return web.json_response(text=to_json(posts))

    async def post(self):
        arguments = await self.request.json()

        async with self.request.app["db"].acquire() as conn:
            succeed, post_id, errors = await create_post(
                conn,
                user_id=arguments.get("user_id"),
                text=arguments.get("text"),
                image=arguments.get("image"),
            )

            if succeed:
                response, status = (
                    await get_post_or_exception(conn, post_id=post_id),
                    201,
                )
            else:
                response, status = {"errors": errors}, 400

        return web.json_response(text=to_json(response), status=status)


class Post(web.View):
    """"""

    async def get(self):
        post_id = int(self.request.match_info.get("post_id"))

        async with self.request.app["db"].acquire() as conn:
            try:
                post = await get_post_or_exception(conn, post_id=post_id)
            except PostNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json(post))

    async def delete(self):
        post_id = int(self.request.match_info.get("post_id"))

        async with self.request.app["db"].acquire() as conn:
            try:
                await delete_post(conn, post_id=post_id)
            except PostNotFoundException as exc:
                return exc.response()

        return web.json_response()

    @staticmethod
    async def likes_count(request: web.Request):
        post_id = int(request.match_info.get("post_id"))

        async with request.app["db"].acquire() as conn:
            try:
                likes_count = await get_posts_likes_count(
                    conn, post_id=post_id
                )
            except PostNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json({"likes_count": likes_count}))

    @staticmethod
    async def comments_count(request: web.Request):
        post_id = int(request.match_info.get("post_id"))

        async with request.app["db"].acquire() as conn:
            try:
                comments_count = await get_posts_comments_count(
                    conn, post_id=post_id
                )
            except PostNotFoundException as exc:
                return exc.response()

        return web.json_response(
            text=to_json({"comments_count": comments_count})
        )

    @staticmethod
    async def comments(request: web.Request):
        post_id = int(request.match_info.get("post_id"))

        async with request.app["db"].acquire() as conn:
            try:
                comments_count = await get_posts_comments(
                    conn, post_id=post_id
                )
            except PostNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json({"comments": comments_count}))
