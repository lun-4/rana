import secrets
import time
import uuid
import sys
import os

import pytest

sys.path.append(os.getcwd())
from rana.auth import hash_password
from rana.run import app as rana_app
from helper import RanaTestClient


@pytest.fixture(name='app')
def app_fixture(event_loop):
    """Yield Rana's app instance.

    This structure was taken off Litecord's test app code.
    """
    # TODO: maybe some function to create app instance
    rana_app._testing = True

    # make sure we're calling the before_serving hooks
    event_loop.run_until_complete(rana_app.startup())

    # https://docs.pytest.org/en/latest/fixture.html#fixture-finalization-executing-teardown-code
    yield rana_app

    # properly teardown
    event_loop.run_until_complete(rana_app.shutdown())


@pytest.fixture
def test_cli(app):
    """Yield the test client."""
    return app.test_client()


@pytest.fixture
async def test_user(app, event_loop):
    """Yield a randomly generated test user.

    After the test is run, the test user is deleted.
    """
    user_id = uuid.uuid4()
    api_key = uuid.uuid4()

    username = secrets.token_hex(6)
    password = secrets.token_hex(6)
    pwd_hash = await hash_password(password, loop=event_loop)

    await app.db.execute("""
    insert into users (id, username, password_hash, created_at)
    values (?, ?, ?, ?)
    """, user_id, username, pwd_hash, time.time())

    await app.db.execute("""
    insert into api_keys (user_id, key)
    values (?, ?)
    """, user_id, api_key)

    yield {'id': user_id, 'api_key': api_key,
           'username': username, 'password': password}

    await app.db.execute("""
    delete from api_keys where user_id = ?
    """, user_id)

    await app.db.execute("""
    delete from users where id = ?
    """, user_id)


@pytest.fixture
async def test_cli_user(test_cli, test_user):
    yield RanaTestClient(test_cli, test_user)
