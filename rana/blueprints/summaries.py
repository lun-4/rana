# stats part of the wakatime api
# https://wakatime.com/developers#stats

import uuid
import datetime
from typing import List, Dict, Any

from quart import Blueprint, request, jsonify, current_app as app

from rana.auth import token_check
from rana.utils import jsonify
from rana.models import validate, SUMMARIES_IN
from rana.database import timestamp_
from rana.errors import BadRequest

from rana.blueprints.durations import calc_durations

bp = Blueprint('summaries', __name__)

# modification of https://stackoverflow.com/a/1060330
def daterange(start_date, delta):
    """Yield dates, making a per-day iteration of the given start date until
    start_date + delta."""
    for day in range(int(delta.days)):
        yield start_date + datetime.timedelta(days=day)

async def _summary_for_day(user_id, date: datetime.datetime) -> Dict[str, Any]:
    """Generate a summary for the day."""
    summary: Dict[str, Any] = {}

    summary['range'] = {
        'date': f'{date.year}-{date.month}-{date.day}',
        'start': date,
        'end': date + datetime.timedelta(hours=23, minutes=59, seconds=59),
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
    args = validate(request.args, SUMMARIES_IN)
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
