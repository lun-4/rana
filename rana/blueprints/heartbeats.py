from quart import Blueprint
from rana.auth import token_check

bp = Blueprint('heartbeats', __name__)

@bp.route('/current/heartbeats', methods=['POST'])
async def post_heartbeat():
    user_id = await token_check()
    return 'uwu', 200

@bp.route('/current/heartbeats.bulk', methods=['POST'])
async def post_many_heartbeats():
    user_id = await token_check()
    return 'uwu', 200

