from aiohttp import web

from api.config import Config
from api.db import init_db
from api.routes import setup_routes
from api.utils.api_specs import setup_api_specs


def main() -> None:
    """Application entrypoint."""

    config = Config.load_config()

    app = init_app(config)

    web.run_app(app)


async def init_app(config: dict) -> web.Application:
    """
    Initialize instance of current application.

    :param config: Configuration for application
    :type config: dict
    :return: Current application
    :rtype: web.Application
    """

    app = web.Application()

    setup_routes(app)

    app["config"] = config

    app["db"] = await init_db(config)

    setup_api_specs(app)

    return app


if __name__ == "__main__":
    main()
