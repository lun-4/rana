from quart import Blueprint, current_app as app
from rana.auth import token_check
from rana.utils import jsonify

bp = Blueprint('users', __name__)

@bp.route('/current', methods=['GET'])
async def get_current_user():
    """Return the currently logged user as a user object."""
    user_id = await token_check()
    user = await app.db.fetch_user(user_id)
    return jsonify(user)
