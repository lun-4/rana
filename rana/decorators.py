import base64
import uuid

from rana.errors import Unauthorized

def auth_route(handler):
    """Enables basic API key authentication."""
    async def new_handler(request, *args, **kwargs):
        try:
            auth = request.headers['authorization']
        except KeyError:
            raise Unauthorized('No API key provided')

        app = request.app
        b64_data = auth.lstrip('Basic ')
        provided_api_key = base64.b64decode(b64_data)

        user_row = await app.db.fetchrow("""
        select user_id from api_keys where api_key = ?
        """, (provided_api_key,))

        if not user_row:
            raise Unauthorized('Invalid API key')

        user_id = uuid.UUID(user_row[0])
        return await handler(request, user_id, *args, **kwargs)

    return new_handler
