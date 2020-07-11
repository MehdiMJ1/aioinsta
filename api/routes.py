from aiohttp import web

from views import hello


def setup_routes(app: web.Application) -> None:
    """
    Setup application routes.

    :param app: Current application
    :type app: web.Application
    """

    router = app.router

    router.add_get("/", hello, name="hello_world")
