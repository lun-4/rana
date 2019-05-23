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


def _dur(row):
    """Duration object from row."""
    return {
        'language': row[1],
        'project': row[2],
        'start': row[3],
        'end': row[4],
    }


async def calc_durations(user_id: uuid.UUID, spans, *, more_raw=False) -> list:
    """Iteraively calculate the durations of a given user based
    on the heartbeats."""
    durations_lst: List[Dict[str, Any]] = []

    rows = await app.db.fetch("""
    SELECT s.user_id, s.language, s.project, s.started_at, s.ended_at
    FROM (
        SELECT user_id, language, project, time AS started_at,
               (LAG(time) OVER (ORDER BY time DESC)) AS ended_at
        FROM heartbeats
        WHERE user_id = ? and time > ? and time < ?
        GROUP BY project, time
        ORDER BY started_at) AS s
    WHERE s.ended_at - s.started_at < 600
    """, user_id, spans[0], spans[1])

    for row in rows:
        # try to fetch the current latest duration in the list
        # and if its duration's end equals to the row's start, we
        # merge the row's end to the duration's end.
        try:
            lat_duration = durations_lst[len(durations_lst) - 1]

            # only update the latest duration if:
            # - the incoming row matches in project name, and
            # - if the incoming row is at MOST 10 minutes separated
            #   from the latest duration
            is_same_project = row[2] == lat_duration['project']
            is_mergeable = (row[3] - lat_duration['end']) < 600

            if is_same_project and is_mergeable:
                lat_duration['end'] = row[4]
            else:
                durations_lst.append(_dur(row))
        except IndexError:
            durations_lst.append(_dur(row))

    def _convert_duration(dur):
        if more_raw:
            return dur

        return {
            'project': dur['project'] or 'Other',
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
