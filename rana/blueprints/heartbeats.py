from sanic import Blueprint
from sanic.response import text

bp = Blueprint('heartbeats', url_prefix='/users')

@bp.post('/current/heartbeats')
async def post_heartbeat(request):
    pass
