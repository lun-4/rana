import pytest
import sys, os

sys.path.append(os.getcwd())

import rana

@pytest.yield_fixture
def app():
    """Yield Rana's app instance."""
    # TODO: maybe some function to create app instance
    yield rana.app

@pytest.fixture
def test_cli(loop, app, sanic_client):
    """Yield the test client."""
    return loop.run_until_complete(sanic_client(app))
