from aiohttp.web import Application

from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from marshmallow import Schema, fields


def setup_api_specs(app: Application) -> None:
    """
    Setup API specification.

    :param app: Application instance
    :type app: Application
    """

    setup_aiohttp_apispec(
        app=app,
        title="My Documentation",
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )

    setup_api_middlewares(app)


def setup_api_middlewares(app: Application) -> None:
    """
    Setup API middlewares.

    :param app: Application instance
    :type app: Application
    """

    app.middlewares.append(validation_middleware)


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str(description="name")


class UserCreateSchema(Schema):
    id = fields.Int()
    password = fields.Str(required=True, description="password")
