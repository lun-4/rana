from sanic import Sanic
from sanic.response import json

from rana.blueprints import group

app = Sanic()
app.blueprint(group)

@app.route("/")
async def test(request):
    return json({"hello": "world"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
