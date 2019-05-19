from sanic import Blueprint
from sanic.response import text

bp = Blueprint('users', url_prefix='/users')

@bp.get('/current')
async def get_current_user(request):
    pass
