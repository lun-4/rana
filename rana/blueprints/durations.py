# durations part of the wakatime api
# https://wakatime.com/developers#durations

import uuid
import datetime
from typing import List, Dict, Any

from quart import Blueprint, request, jsonify, current_app as app

from rana.auth import token_check
from rana.utils import jsonify
from rana.models import validate, DURATIONS_IN
from rana.database import timestamp_

bp = Blueprint('durations', __name__)


def _isofy(posix_tstamp: int) -> str:
    """Return an ISO timestamp out of a POSIX integer timestamp."""
    return datetime.datetime.fromtimestamp(posix_tstamp).isoformat()


async def calc_durations(user_id: uuid.UUID, spans) -> list:
    """Iteraively calculate the durations of a given user based
    on the heartbeats."""
    cur_tstamp = spans[0]
    max_time = spans[1]
    durations_lst: List[Dict[str, Any]] = []

    while True:
        if cur_tstamp >= spans[1]:
            break

        # TODO: this is broken
        row = await app.db.fetchrow("""
        select max(time), min(time), project
        from heartbeats
        where time > ? and time < ? and user_id = ?
        group by project
        limit 1
        """, cur_tstamp.timestamp(), max_time.timestamp(), user_id)

        if row is None:
            break

        durations_lst.append({
            'start': _isofy(row[0]),
            'end': _isofy(row[1]),
            'project': row[2],
        })

        cur_tstamp = datetime.datetime.fromtimestamp(row[0])

    return durations_lst


async def durations(user_id: uuid.UUID, args: dict):
    """Calculate user's durations for a given day (in args.date).

    Returns the JSON response for the API.
    """
    spans = args['date'].timespans
    durations_lst = await calc_durations(user_id, spans)

    return jsonify(durations_lst, extra={
        'branches': ['master'],
        'start': spans[0].isoformat(),
        'end': spans[1].isoformat(),
    })


@bp.route('/current/durations')
async def current_user_durations():
    user_id = await token_check()
    args = validate(dict(request.args), DURATIONS_IN)
    return await durations(user_id, args)
