# stats part of the wakatime api
# https://wakatime.com/developers#stats

import uuid
import datetime
from collections import Counter
from typing import List, Dict, Any

from quart import Blueprint, request, jsonify, current_app as app

from rana.auth import token_check
from rana.utils import jsonify
from rana.models import validate, SUMMARIES_IN
from rana.database import timestamp_
from rana.errors import BadRequest

from rana.blueprints.durations import calc_durations, convert_tz

bp = Blueprint('summaries', __name__)

# modification of https://stackoverflow.com/a/1060330
def daterange(start_date, delta):
    """Yield dates, making a per-day iteration of the given start date until
    start_date + delta."""
    for day in range(int(delta.days) + 1):
        yield start_date + datetime.timedelta(days=day)


def _process_durations(durations: List[Dict[str, Any]],
                       counter_key: str, value_func) -> Counter:
    counter: Counter = Counter()

    for duration in durations:
        counter[counter_key] = value_func(duration)

    return counter


def _do_summary_list(summary, sum_key: str, counter: Counter,
                     total_seconds):
    summary[sum_key] = []

    for name, seconds in counter.most_common():
        summary[sum_key].append({
            'name': name,
            'percent': round(seconds / total_seconds, 2) * 100,
            'total_seconds': seconds,
        })


def _day_summary_projects(summary: Dict[str, Any],
                          durations: List[Dict[str, Any]]):
    projects_counter: Counter = Counter()
    langs_counter: Counter = Counter()
    total_seconds = 0

    for duration in durations:
        duration_secs = duration['end'] - duration['start']

        projects_counter[duration['project']] += duration_secs
        langs_counter[duration['language']] += duration_secs
        total_seconds += duration_secs

    summary['grand_total'] = {
        'total_seconds': total_seconds,
    }

    # add projects list and languages list
    _do_summary_list(summary, 'projects', projects_counter, total_seconds)
    _do_summary_list(summary, 'languages', langs_counter, total_seconds)


async def _summary_for_day(user_id, date: datetime.datetime) -> Dict[str, Any]:
    """Generate a summary for the day.
    Given date is assumed not-timezone-aware and on the user's
    local timezone."""
    summary: Dict[str, Any] = {}

    user_tz = await app.db.fetch_user_tz(user_id)
    date = convert_tz(date, user_tz, 'UTC')

    dur_start = date.timestamp()
    day_delta = datetime.timedelta(hours=23, minutes=59, seconds=59)
    dur_end = (date + day_delta).timestamp()

    durations = await calc_durations(
        user_id, (dur_start, dur_end), more_raw=True)

    _day_summary_projects(summary, durations)

    summary['range'] = {
        'date': f'{date.year}-{date.month}-{date.day}',
        'start': date.isoformat(),
        'end': (date + day_delta).isoformat(),
    }

    return summary


async def make_summary(user_id: uuid.UUID, start_date,
                       delta) -> List[Dict[str, Any]]:
    """Make a summary for the given date and ending at the date + delta."""
    data: List[Dict[str, Any]] = []

    for date in daterange(start_date, delta):
        day_data = await _summary_for_day(user_id, date)
        data.append(day_data)

    return data


@bp.route('/current/summaries')
async def user_summary():
    """Generate a user summary given the start and end dates of the summary.

    The max timedelta for a summary is 31 days.
    """
    user_id = await token_check()
    args = validate(dict(request.args), SUMMARIES_IN)
    start_date, end_date = args['start'].date, args['end'].date

    if start_date > end_date:
        raise BadRequest('Invalid date range.')

    delta = end_date - start_date
    if delta.days >= 32:
        raise BadRequest('Too many requested days.')

    data = await make_summary(user_id, start_date, delta)

    return jsonify(data, extra={
        'start': start_date.isoformat(),
        'end': end_date.isoformat(),
    })
