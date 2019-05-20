import logging
import re
from typing import Union, Dict, List, Optional

from cerberus import Validator
from quart import current_app as app

from rana.errors import BadRequest

log = logging.getLogger(__name__)

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_ ]{2,30}$', re.A)


class RanaValidator(Validator):
    """Main validator class for Litecord, containing custom types."""
    def _validate_type_username(self, value: str) -> bool:
        """Validate against the username regex."""
        return bool(USERNAME_REGEX.match(value))

    def _validate_type_password(self, value: str) -> bool:
        """Validate a password. Max 2048 chars. Min 1."""
        return 1 <= len(value) <= 2048

    def _validate_type_entity_type(value):
        return value in ('app', 'file', 'domain')


def validate(reqjson: Union[Dict, List], schema: Dict,
             raise_err: bool = True) -> Optional[Dict]:
    """Validate the given user-given data against a schema, giving the
    "correct" version of the document, with all defaults applied.

    Parameters
    ----------
    reqjson:
        The input data
    schema:
        The schema to validate reqjson against
    raise_err:
        If we should raise a BadRequest error when the validation
        fails. Default is true.
    """
    validator = RanaValidator(schema)

    try:
        valid = validator.validate(reqjson)
    except Exception:
        log.exception('Error while validating')
        raise Exception(f'Error while validating: {reqjson}')

    if not valid:
        errs = validator.errors
        log.warning('Error validating doc %r: %r', reqjson, errs)

        if raise_err:
            raise BadRequest(f'bad payload: {errs!r}')

        return None

    return validator.document

HEARTBEAT_MODEL = {
    'entity': {'type': 'string'},
    'type': {'type': 'entity_type'},
    'category': {'type': 'activity_type', 'nullable': True},
    'time': {'coerce': float},

    'project': {'type': 'string', 'required': False},
    'branch': {'type': 'string', 'required': False},
    'language': {'type': 'string', 'required': False},

    'dependencies': {
        'type': 'list', 'schema': {'type': 'string'}, 'required': False},

    'lines': {'coerce': int, 'depedencies': ['type']},
    'lineno': {'coerce': int, 'depedencies': ['type'], 'required': False},
    'cursorpos': {'coerce': int, 'depedencies': ['type'], 'required': False},
    'is_write': {'coerce': bool, 'depedencies': ['type'], 'required': False},
}
