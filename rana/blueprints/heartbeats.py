import uuid
import pathlib
from quart import Blueprint, request, jsonify, current_app as app
from typing import Optional

from rana.auth import token_check
from rana.errors import BadRequest
from rana.models import validate, HEARTBEAT_MODEL
from rana.utils import jsonify as rjsonify

bp = Blueprint('heartbeats', __name__)


async def fetch_machine(user_id) -> uuid.UUID:
    """Return the Machine ID for the given request.
    Creates a new machine for the given user if the given
    X-Machine-Name value is new.
    """
    try:
        mach_name = request.headers['x-machine-name']
    except KeyError:
        mach_name = 'root'

    mach_id = await app.db.fetchval("""
    select id from machines where name = ? and user_id = ?
    """, mach_name, user_id)

    if mach_id is not None:
        return mach_id

    mach_id = uuid.uuid4()

    await app.db.execute("""
    insert into machines (id, user_id, name)
    values (?, ?, ?)
    """, mach_id, user_id, mach_name)

    return mach_id


EXTENSIONS = {
    'zig': 'Zig',
}


def lang_from_ext(extension: str) -> Optional[str]:
    """Return a heartbeat language out of its extension.

    Used to give results for languages that aren't as commonplace.
    """
    return EXTENSIONS.get(extension)


async def _process_hb(user_id, machine_id, heartbeat):
    heartbeat_id = uuid.uuid4()

    if heartbeat.get('language') is None and heartbeat.get('type') == 'file':
        entity_path = heartbeat['entity']

        if entity_path.lower().startswith('c:'):
            path = pathlib.PureWindowsPath(entity_path)
        else:
            path = pathlib.PurePosixPath(entity_path)

        heartbeat['language'] = lang_from_ext(path.suffix)

    await app.db.execute(
        """
        insert into heartbeats (id, user_id, machine_id,
            entity, type, category, time,
            is_write, project, branch, language, lines, lineno, cursorpos)
        values
            (?, ?, ?,
             ?, ?, ?,
             ?, ?, ?,
             ?, ?, ?,
             ?, ?)
        """,
        heartbeat_id, user_id, machine_id,
        heartbeat['entity'], heartbeat['type'], heartbeat['category'],
        heartbeat['time'], heartbeat['is_write'], heartbeat['project'],
        heartbeat['branch'], heartbeat['language'], heartbeat['lines'],
        heartbeat['lineno'], heartbeat['cursorpos'])

    return await app.db.fetch_heartbeat(heartbeat_id)


@bp.route('/current/heartbeats', methods=['POST'])
async def post_heartbeat():
    user_id = await token_check()

    raw_json = await request.get_json()
    if not isinstance(raw_json, list):
        raise BadRequest('no heartbeat list provided')

    j = validate(raw_json, HEARTBEAT_MODEL)
    machine_id = await fetch_machine(user_id)
    heartbeat = await _process_hb(user_id, machine_id, j)
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

    machine_id = await fetch_machine(user_id)

    res = []
    for heartbeat in j:
        res.append(
            await _process_hb(user_id, machine_id, heartbeat)
        )

    return jsonify({
        'responses': res
    }), 201
