class RanaError(Exception):
    """Represents a generic error in Rana."""

    status_code = 500

    @property
    def message(self):
        """Return the error message for the given error."""
        return self.args[0]


class BadRequest(RanaError):
    status_code = 400


class Unauthorized(RanaError):
    status_code = 401


class Forbidden(RanaError):
    status_code = 403
