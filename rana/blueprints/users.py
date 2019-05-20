from quart import Blueprint, current_app as app
from rana.decorators import auth_route
from rana.utils import jsonify

bp = Blueprint('users', __name__)

@bp.route('/current', methods=['GET'])
@auth_route
async def get_current_user(user_id):
    """Return the currently logged user as a user object."""
    user = await app.db.fetch_user(user_id)
    return jsonify(user)
