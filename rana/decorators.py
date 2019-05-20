import base64
import uuid

from quart import current_app as app, request
from rana.errors import Unauthorized
