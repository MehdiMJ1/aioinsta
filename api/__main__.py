from aiohttp import web

from routes import setup_routes


def main() -> None:
    """Application entrypoint."""

    app = web.Application()

    setup_application(app)

    web.run_app(app)


def setup_application(app: web.Application) -> None:
    """
    Setup components of the application.

    :param app: Current application
    :type app: web.Application
    """

    setup_routes(app)


if __name__ == "__main__":
    main()
