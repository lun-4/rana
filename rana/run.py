import logging

from sanic import Sanic
from sanic.response import json

from rana.blueprints import group
from rana.errors import RanaError
from rana.database import Database

app = Sanic()
log = logging.getLogger(__name__)
app.blueprint(group)
app.db = Database(app)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.exception(RanaError)
async def rana_error_handler(request, exception: RanaError):
    """Exception handler to convert RanaError exceptions into the proper
    JSON body + status code."""
    return json({
        'error': exception.message
    }, status=exception.status_code)


@app.exception(Exception)
async def rana_generic_err(request, exception):
    log.exception('Error on request: %r', exception)
    return json({
        'error': repr(exception),
    }, status=500)


@app.listener('after_server_stop')
async def teardown_func(app_, loop):
    await app.db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=8000)
