# leaders part of the wakatime api
# https://wakatime.com/developers#leaders

import datetime
import logging

from math import ceil
from collections import Counter
from typing import List, Dict, Any

from quart import Blueprint, request, jsonify, current_app as app

from rana.auth import token_check
from rana.utils import jsonify
from rana.models import validate, LEADERS_IN

from rana.blueprints.durations import durations_from_rows

bp = Blueprint('leaders', __name__)
log = logging.getLogger(__name__)

USERS_PER_PAGE = 20

async def calc_leaders(max_users=50, language=None):
    """Calculate the global/language leaderboard."""
    utcnow = datetime.datetime.utcnow()

    # remove hour/minute/second
    utcnow = datetime.datetime(
        year=utcnow.year, month=utcnow.month, day=utcnow.day)

    start = (utcnow - datetime.timedelta(days=7)).timestamp()
    end = utcnow.timestamp()

    args = [language] if language else []
    lang_clause = 'and language = ?'

    rows = await app.db.fetch(f"""
    SELECT s.user_id, s.language, s.project, s.started_at, s.ended_at
    FROM (
        SELECT user_id, language, project, time AS started_at,
               (LAG(time) OVER (ORDER BY time DESC)) AS ended_at
        FROM heartbeats
        WHERE time > ? and time < ? {lang_clause}
        GROUP BY user_id, project, time
        ORDER BY started_at) AS s
    WHERE s.ended_at - s.started_at < 600
    """, start, end, *args)

    durations = durations_from_rows(rows, do_user=True)
    log.debug('%d rows, %d global durations', len(rows), len(durations))

    counter = Counter()
    for duration in durations:
        total_seconds = duration['end'] - duration['start']
        counter[duration['user_id']] += total_seconds

    return (start, end), counter.most_common(max_users)



@bp.route('', methods=['GET'])
async def get_leaders():
    user_id = await token_check()
    args = validate(dict(request.args), LEADERS_IN)

    # NOTE: this is bad bc the pages dont actually work on
    # removing the query hell
    time_range, leaders = await calc_leaders(
        language=args.get('language'))

    leaders_count = len(leaders)
    leaders_idx = args['page'] * USERS_PER_PAGE
    leaders = leaders[leaders_idx:leaders_idx + USERS_PER_PAGE]

    data = []

    return jsonify(data, extra={
        'user': await app.db.fetch_user_simple(user_id),
        'current_user': {},
        'range': {
            'start_date': time_range[0].isoformat(),
            'end_date': time_range[1].isoformat(),
        },
        'language': args.get('language'),

        'page': args['page'],
        'total_pages': ceil(leaders_count / USERS_PER_PAGE),
    })
