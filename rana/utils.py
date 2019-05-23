import datetime
import pprint
from typing import Any, Dict, Tuple, Sequence, Optional
from quart import jsonify as quart_jsonify


class Date:
    """Represents a single date from the WakaTime API."""
    def __init__(self, value):
        self.value = value
        components = value.split('-')
        if len(components) != 3:
            raise ValueError('invalid date format')

        try:
            year, month, day = map(int, components)
        except (TypeError, ValueError):
            raise ValueError('invalid date values')

        self.date = datetime.datetime(year, month, day)

    @property
    def timespans(self) -> Tuple[float, float]:
        """Return the start and end POSIX timestamp for the given date.

        The given datetime objects should have a timedelta of approximately
        24 hours.
        """
        end_ts = self.date + datetime.timedelta(hours=23, minutes=59)
        return self.date.timestamp(), end_ts.timestamp()



def jsonify(data: Any, *, extra=None) -> Dict[str, Any]:
    """Wrap given data in a json object containing a key named data.

    This is necessary to comply with the Wakatime API request/reponse format.
    """
    extra = extra or {}
    extra['data'] = data
    pprint.pprint(extra)
    return quart_jsonify(extra)


def index_by_func(function, indexable: Sequence[Any]) -> Optional[int]:
    """Search in an idexable and return the index number
    for an iterm that has func(item) = True."""
    for index, item in enumerate(indexable):
        if function(item):
            return index

    return None
