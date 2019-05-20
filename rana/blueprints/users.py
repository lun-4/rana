from sanic import Blueprint

from rana.decorators import auth_route
from rana.utils import json

bp = Blueprint('users', url_prefix='/users')

@bp.get('/current')
@auth_route
async def get_current_user(request, user_id):
    """Return the currently logged user as a user object."""
    user = await request.app.db.fetch_user(user_id)
    return json(user)
