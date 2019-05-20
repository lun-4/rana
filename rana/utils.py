from typing import Any, Dict
from quart import jsonify as quart_jsonify


def jsonify(data: Any) -> Dict[str, Any]:
    """Wrap given data in a json object containing a key named data.

    This is necessary to comply with the Wakatime API request/reponse format.
    """
    return quart_jsonify({'data': data})
