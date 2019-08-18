import datetime
from typing import Any, Dict, Tuple, Sequence, Optional
from quart import jsonify as quart_jsonify


class Date:
    """Represents a single date from the WakaTime API."""

    def __init__(self, value):
        self.value = value

        if value == "today":
            utcnow = datetime.datetime.utcnow()
            self.date = datetime.datetime(
                year=utcnow.year, month=utcnow.month, day=utcnow.day
            )

            return

        components = value.split("-")
        if len(components) != 3:
            raise ValueError("invalid date format")

        try:
            year, month, day = map(int, components)
        except (TypeError, ValueError):
            raise ValueError("invalid date values")

        self.date = datetime.datetime(year, month, day)

    @property
    def end_dt(self):
        return self.date + datetime.timedelta(hours=23, minutes=59)

    @property
    def timespans(self) -> Tuple[float, float]:
        """Return the start and end POSIX timestamp for the given date.

        The given datetime objects should have a timedelta of approximately
        24 hours.
        """
        return self.date.timestamp(), self.end_dt.timestamp()

    @property
    def spans_as_dt(self) -> Tuple[datetime.datetime, datetime.datetime]:
        return self.date, self.end_dt


def jsonify(data: Any, *, extra=None) -> Dict[str, Any]:
    """Wrap given data in a json object containing a key named data.

    This is necessary to comply with the Wakatime API request/reponse format.
    """
    extra = extra or {}
    extra["data"] = data
    return quart_jsonify(extra)
