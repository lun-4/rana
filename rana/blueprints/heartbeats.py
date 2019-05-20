import uuid
from quart import Blueprint, request, jsonify

from rana.auth import token_check
from rana.errors import BadRequest
from rana.models import validate, HEARTBEAT_MODEL
from rana.utils import jsonify as rjsonify

bp = Blueprint('heartbeats', __name__)


async def _process_hb(user_id, heartbeat):
    heartbeat_id = uuid.uuid4()
    return {}


@bp.route('/current/heartbeats', methods=['POST'])
async def post_heartbeat():
    user_id = await token_check()

    raw_json = await request.get_json()
    if not isinstance(raw_json, list):
        raise BadRequest('no heartbeat list provided')

    j = validate(raw_json, HEARTBEAT_MODEL)
    heartbeat = await _process_hb(user_id, j)
    return jsonify(heartbeat), 201


@bp.route('/current/heartbeats.bulk', methods=['POST'])
async def post_many_heartbeats():
    user_id = await token_check()

    raw_json = await request.get_json()
    if not isinstance(raw_json, list):
        raise BadRequest('no heartbeat list provided')

    j = validate({'hbs': raw_json}, {
        'hbs': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': HEARTBEAT_MODEL
            }
        }
    })['hbs']

    res = []
    for heartbeat in j:
        res.append(
            await _process_hb(user_id, heartbeat)
        )

    return jsonify({
        'responses': res
    }), 201
