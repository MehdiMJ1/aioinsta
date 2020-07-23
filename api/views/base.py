from aiohttp import web

from api.utils.exceptions import RecordNotFoundException
from api.utils.json_serializers import to_json


class BaseWebView(web.View):
    """Default view for getting and deleting single item."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None
        self.get_func = None
        self.delete_func = None

    async def get(self):
        """Processing of GET request."""

        field_id = int(self.request.match_info.get(self.field))

        async with self.request.app["db"].acquire() as conn:
            try:
                obj = await self.get_func(conn, **{self.field: field_id})
            except RecordNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json(obj))

    async def delete(self):
        """Processing of DELETE request."""

        field_id = int(self.request.match_info.get(self.field))

        async with self.request.app["db"].acquire() as conn:
            try:
                result = await self.delete_func(conn, **{self.field: field_id})
            except RecordNotFoundException as exc:
                return exc.response()

        return web.json_response(text=to_json({"deleted": result}))


class BaseListWebView(BaseWebView):
    """Default view for getting list of items or create new one."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_list_func = None
        self.create_func = None
        self.create_fields = ()

    async def get(self):
        """Processing of GET request."""

        async with self.request.app["db"].acquire() as conn:
            objects = await self.get_list_func(conn)

        return web.json_response(text=to_json(objects))

    async def post(self):
        """Processing of POST request."""

        json_data = await self.request.json()

        arguments = {
            key: value
            for key, value in json_data.items()
            if key in self.create_fields
        }

        async with self.request.app["db"].acquire() as conn:
            obj_id = await self.create_func(
                conn,
                **arguments
            )
            obj = await self.get_func(conn, **{self.field: obj_id})

        return web.json_response(text=to_json(obj))
