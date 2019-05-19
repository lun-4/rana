import base64

class RanaTestClient:
    def __init__(self, test_cli, test_user):
        self.cli = test_cli
        self.user = test_user

    def _inject_auth(self, kwargs: dict) -> list:
        """Inject the test user's API key into the
        test request before passing the request on
        to the underlying TestClient."""
        headers = kwargs.get('headers', {})
        api_key = self.user['api_key']
        api_key_b64 = base64.b64encode(api_key).decode()
        headers['authorization'] = f'Basic {api_key_b64}'

        return headers

    async def get(self, *args, **kwargs):
        """Send a GET request."""
        kwargs['headers'] = self._inject_auth(kwargs)
        return await self.cli.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        """Send a POST request."""
        kwargs['headers'] = self._inject_auth(kwargs)
        return await self.cli.post(*args, **kwargs)
