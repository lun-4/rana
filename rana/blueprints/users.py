from sanic import Blueprint
from sanic.response import json

from rana.decorators import auth_route

bp = Blueprint('users', url_prefix='/users')

@bp.get('/current')
@auth_route
async def get_current_user(request, user_id):
    user = await request.app.db.fetch_user(user_id)
    return json(user)
