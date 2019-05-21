# durations part of the wakatime api
# https://wakatime.com/developers#durations

import uuid
import pathlib
from quart import Blueprint, request, jsonify, current_app as app
from typing import Optional

from rana.auth import token_check
from rana.errors import BadRequest
from rana.utils import jsonify
from rana.models import validate, DURATIONS_IN

bp = Blueprint('durations', __name__)

async def durations(user_id: uuid.UUID, args: dict):
    """Calculate user's durations for a given day (in args.date).

    Returns the JSON response for the API.
    """
    pass

@bp.route('/current/durations')
async def current_user_durations():
    user_id = await token_check()
    args = validate(request.args, DURATIONS_IN)
    return await durations(user_id, args)
