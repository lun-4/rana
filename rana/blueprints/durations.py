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
    durations_lst: List[Dict[str, Any]] = []

    rows = await app.db.fetch("""
    SELECT s.user_id, s.project, s.started_at, s.ended_at
    FROM (
        SELECT user_id, project, time AS started_at,
               (LAG(time) OVER (ORDER BY time DESC)) AS ended_at
        FROM heartbeats
        WHERE user_id = ? and time > ? and time < ?
        GROUP BY user_id, project, time
        ORDER BY started_at) AS s
    WHERE s.ended_at - s.started_at < 600
    """, user_id, spans[0], spans[1])

    for row in rows:
        # try to fetch the current latest duration in the list
        # and if its duration's end equals to the row's start, we
        # merge the row's end to the duration's end.
        try:
            lat_duration = durations_lst[len(durations_lst) - 1]

            # only update if they're equal, effectively merging them
            if (row[3] - lat_duration['end']) < 600:
                lat_duration['end'] = row[3]
            else:
                durations_lst.append({
                    'project': row[1],
                    'start': row[2],
                    'end': row[3],
                })
        except IndexError:
            durations_lst.append({
                'project': row[1],
                'start': row[2],
                'end': row[3],
            })

    def _convert_duration(dur):
        return {
            'project': dur['project'],
            'start': _isofy(dur['start']),
            'end': _isofy(dur['end']),
        }

    return list(map(_convert_duration, durations_lst))


async def durations(user_id: uuid.UUID, args: dict):
    """Calculate user's durations for a given day (in args.date).

    Returns the JSON response for the API.
    """
    spans = args['date'].timespans
    durations_lst = await calc_durations(user_id, spans)

    return jsonify(durations_lst, extra={
        'branches': ['master'],
        'start': _isofy(spans[0]),
        'end': _isofy(spans[1]),
    })


@bp.route('/current/durations')
async def current_user_durations():
    user_id = await token_check()
    args = validate(dict(request.args), DURATIONS_IN)
    return await durations(user_id, args)
