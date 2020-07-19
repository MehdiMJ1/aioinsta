from aiohttp import web

from api.logic.posts import (
    get_post_or_exception,
    get_posts,
    create_post,
    delete_post,
    get_posts_likes_count,
    get_posts_comments_count,
    get_posts_comments,
    PostNotFoundException
)
from api.logic.users import (
    get_user_or_exception
)
from api.utils.json_serializers import to_json
from api.utils.exceptions import RecordNotFoundException


async def hello(request: web.Request) -> web.Response:
    """
    First, single and test view of application.

    :param request: Input request
    :type request: web.Request
    :return: Static json string `{"status": "OK"}`
    :rtype: web.Response
    """

    return web.json_response(text=to_json({"status": "OK"}))


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
                response, status = await get_post_or_exception(
                    conn, post_id=post_id
                ), 201
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

    """async def put(self):
        post_id_ = int(self.request.match_info.get("post_id"))
        arguments = await self.request.json()

        async with self.request.app["db"].acquire() as conn:
            # Todo: change it as put method, not patch
            try:
                succeed, post_id, errors = await edit_post(
                    conn,
                    post_id=post_id_,
                    user_id=arguments.get("user_id"),
                    text=arguments.get("text"),
                    image=arguments.get("image"),
                )
            except PostNotFoundException as exc:
                return exc.response()

            if succeed:
                response, status = await get_post_or_exception(
                    conn, post_id=post_id
                ), 200
            else:
                response, status = {"errors": errors}, 400

        return web.json_response(text=to_json(response), status=status)"""

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

        return web.json_response(
            text=to_json({"comments": comments_count})
        )


"""class User(web.View):
    """"""

    async def get(self):
        user_id = int(self.request.match_info.get("user_id"))

        async with self.request.app["db"].acquire() as conn:
            try:
                user = await get_user_or_exception(conn, user_id=user_id)
            except UserNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json(user))"""


class BaseWebView(web.View):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None
        self.get_func = None

    async def get(self):
        field_id = int(self.request.match_info.get(self.field))

        async with self.request.app["db"].acquire() as conn:
            try:
                obj = await self.get_func(
                    conn, **{self.field: field_id}
                )
            except RecordNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json(obj))


class User(BaseWebView):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = "user_id"
        self.get_func = get_user_or_exception
        self.put_func = get_user_or_exception
        self.delete_func = get_user_or_exception
