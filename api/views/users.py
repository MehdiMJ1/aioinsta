from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema
)
from marshmallow import Schema, fields

from api.logic.users import (
    create_user,
    delete_user,
    get_users,
    get_user_or_exception,
)
from api.views.base import BaseListWebView, BaseWebView


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str(description="name")


class UserCreateSchema(Schema):
    id = fields.Int()
    password = fields.Str(required=True, description="password")


class User(BaseWebView):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = "user_id"
        self.get_func = get_user_or_exception
        self.delete_func = delete_user


class UserList(BaseListWebView, User):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_list_func = get_users
        self.create_func = create_user
        self.create_fields = (
            "username", "name", "email", "password", "description"
        )

    @docs(
        tags=["mytag"],
        summary="Test method summary",
        description="Test method description",
    )
    @request_schema(UserCreateSchema())
    @response_schema(UserSchema, 200)
    async def post(self):
        await super().post()
