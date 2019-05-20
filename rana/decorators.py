import base64
import uuid

from quart import current_app as app, request
from rana.errors import Unauthorized

def auth_route(handler):
    """Enables basic API key authentication."""
    async def new_handler(*args, **kwargs):
        try:
            auth = request.headers['authorization']
        except KeyError:
            raise Unauthorized('No API key provided')

        b64_data = auth.lstrip('Basic ')
        provided_api_key = base64.b64decode(b64_data).decode()
        api_key = str(uuid.UUID(provided_api_key))

        user_row = await app.db.fetchrow("""
        select user_id from api_keys where key = ?
        """, (api_key,))

        if not user_row:
            raise Unauthorized('Invalid API key')

        user_id = uuid.UUID(user_row[0])
        return await handler(user_id, *args, **kwargs)

    return new_handler
