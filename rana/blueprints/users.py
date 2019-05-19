from sanic import Blueprint
from sanic.response import text

from rana.decorators import auth_route

bp = Blueprint('users', url_prefix='/users')

@bp.get('/current')
@auth_route
async def get_current_user(request):
    return text('uwu')
