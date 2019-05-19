from sanic import Blueprint
from sanic.response import text

from rana.decorators import auth_route

bp = Blueprint('heartbeats', url_prefix='/users')

@bp.post('/current/heartbeats')
@auth_route
async def post_heartbeat(request, user_id):
    return text('uwu')

@bp.post('/current/heartbeats.bulk')
@auth_route
async def post_many_heartbeats(request, user_id):
    return text('uwu')
