import json

from aiohttp import web

from api.routes import setup_routes


async def test_hello(aiohttp_client):
    app = web.Application()

    setup_routes(app)

    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert json.loads(text).get("status") == "OK"
