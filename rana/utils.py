from typing import Any, Dict
from quart import jsonify as quart_jsonify


def jsonify(data: Any, *, extra=None) -> Dict[str, Any]:
    """Wrap given data in a json object containing a key named data.

    This is necessary to comply with the Wakatime API request/reponse format.
    """
    extra = extra or {}
    extra['data'] = data
    return quart_jsonify(extra)
