# leaders part of the wakatime api
# https://wakatime.com/developers#leaders

import datetime
import logging

from math import ceil
from collections import Counter, defaultdict
from typing import List, Dict, Any

from quart import Blueprint, request, current_app as app

from rana.auth import token_check
from rana.utils import jsonify
from rana.models import validate, LEADERS_IN

from rana.blueprints.durations import durations_from_rows

bp = Blueprint("leaders", __name__)
log = logging.getLogger(__name__)

USERS_PER_PAGE = 20


async def calc_leaders(language=None):
    """Calculate the global/language leaderboard."""
    utcnow = datetime.datetime.utcnow()

    # remove hour/minute/second
    utcnow = datetime.datetime(year=utcnow.year, month=utcnow.month, day=utcnow.day)

    start = utcnow - datetime.timedelta(days=7)
    end = utcnow

    args = [language] if language else []
    lang_clause = "and language = $3" if language else ""

    rows = await app.db.fetch(
        f"""
    SELECT s.user_id, s.language, s.project, s.started_at, s.ended_at
    FROM (
        SELECT user_id, language, project, time AS started_at,
               (LAG(time) OVER (ORDER BY time DESC)) AS ended_at
        FROM heartbeats
        WHERE time > $1 and time < $2 and is_write = true {lang_clause}
        GROUP BY user_id, language, project, time
        ORDER BY started_at) AS s
    WHERE s.ended_at - s.started_at < 600
    """,
        start.timestamp(),
        end.timestamp(),
        *args,
    )

    durations = durations_from_rows(rows, do_user=True)
    log.debug("%d rows, %d global durations", len(rows), len(durations))

    leader_data = defaultdict(lambda: Counter())

    for duration in durations:
        user_id = duration["user_id"]
        lang = duration["language"] or "Other"
        total_seconds = duration["end"] - duration["start"]

        leader_data[user_id][lang] += total_seconds

    return (start, end), leader_data


async def rank_for_user(leader_data, global_rank, sorted_leaders, user_id):
    """Give rank info for given user."""
    user = await app.db.fetch_user_simple(user_id)
    if user is None:
        return

    rank = sorted_leaders.index(user_id)
    langs_counts = {
        lang: tot_secs for lang, tot_secs in leader_data[user_id].most_common()
    }

    return {
        "rank": rank,
        "running_total": {
            # api clients can check the start and end of the
            # leaderboard ranges and divide this given total_seconds
            # by the amount of days on that range.
            "total_seconds": global_rank[user_id],
            "languages": langs_counts,
        },
        "user": user,
    }


@bp.route("", methods=["GET"])
async def get_leaders():
    user_id = await token_check()
    args = validate(dict(request.args), LEADERS_IN)

    # NOTE: this is bad bc the pages dont actually work on
    # removing the query hell
    time_range, leader_data = await calc_leaders(language=args.get("language"))

    global_rank = {
        user_id: sum(val for _, val in lang_counter.most_common())
        for user_id, lang_counter in leader_data.items()
    }

    leaders_count = len(global_rank)
    leaders_idx = args["page"] * USERS_PER_PAGE
    sorted_leaders = sorted(global_rank.keys(), key=lambda uid: global_rank[uid])
    leader_ids = list(sorted_leaders)[leaders_idx : leaders_idx + USERS_PER_PAGE]

    data = []

    for user_id in leader_ids:
        data.append(
            await rank_for_user(leader_data, global_rank, sorted_leaders, user_id)
        )

    return jsonify(
        data,
        extra={
            "user": await app.db.fetch_user_simple(user_id),
            "current_user": await rank_for_user(
                leader_data, global_rank, sorted_leaders, user_id
            ),
            "range": {
                "start_date": time_range[0].isoformat(),
                "end_date": time_range[1].isoformat(),
            },
            "language": args.get("language"),
            "page": args["page"],
            "total_pages": ceil(leaders_count / USERS_PER_PAGE),
        },
    )
