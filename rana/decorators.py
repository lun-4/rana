from rana.errors import Unauthorized

def auth_route(handler):
    """Enables basic API key authentication."""
    async def new_handler(request, *args, **kwargs):
        auth = request.headers['authorization']

        if not auth:
            raise Unauthorized('No token provided')

        # TODO: handle Authorication

        return await handler(request, *args, **kwargs)

    return new_handler
