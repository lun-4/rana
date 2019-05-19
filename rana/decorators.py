from rana.errors import Unauthorized

def auth_route(handler):
    """Enables basic API key authentication."""
    async def new_handler(request, *args, **kwargs):
        try:
            auth = request.headers['authorization']
        except KeyError:
            raise Unauthorized('No token provided')

        # TODO: handle Authorication

        return await handler(request, *args, **kwargs)

    return new_handler
