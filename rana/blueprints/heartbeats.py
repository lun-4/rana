from quart import Blueprint
from rana.decorators import auth_route

bp = Blueprint('heartbeats', __name__)

@bp.route('/current/heartbeats', methods=['POST'])
@auth_route
async def post_heartbeat(user_id):
    return 200, 'uwu'

@bp.route('/current/heartbeats.bulk', methods=['POST'])
@auth_route
async def post_many_heartbeats(user_id):
    return 200, 'uwu'

