import json

from aiohttp import web


async def hello(request: web.Request) -> web.Response:
    """
    First, single and test view of application.

    :param request: Input request
    :type request: web.Request
    :return: Static json string `{"status":"OK"}`
    :rtype: web.Response
    """

    return web.json_response(text=json.dumps({"status": "OK"}))
