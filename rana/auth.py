import binascii
import asyncio
import base64
import uuid

import bcrypt
from quart import request, current_app as app

from rana.errors import Unauthorized


async def hash_password(password: str, *, loop=None) -> str:
    """Generate a hash for any given password"""
    loop = loop or asyncio.get_event_loop()

    password_bytes = bytes(password, 'utf-8')
    hashed = loop.run_in_executor(
        None, bcrypt.hashpw, password_bytes, bcrypt.gensalt(14)
    )

    return (await hashed).decode('utf-8')


async def check_password(pwd_hash_s: str, password_s: str, *, loop=None):
    """Check if any given two passwords match. Raises Unauthroized on
    invalid password."""
    loop = loop or asyncio.get_event_loop()
    pwd_hash = pwd_hash_s.encode()
    password = password_s.encode()

    valid = await loop.run_in_executor(
        None, bcrypt.checkpw, pwd_hash, password)

    if not valid:
        raise Unauthorized('invalid password')


async def token_check():
    """Check if the given API key in the authorization header is valid."""
    try:
        auth = request.headers['Authorization']
    except KeyError:
        raise Unauthorized('No API key provided')

    try:
        b64_data = auth.lstrip('Basic ')
        provided_api_key = base64.b64decode(b64_data).decode()
        api_key = str(uuid.UUID(provided_api_key))
    except (binascii.Error, ValueError):
        raise Unauthorized('Invalid API key provided')

    user_row = await app.db.fetchrow("""
    select user_id from api_keys where key = ?
    """, api_key)

    if not user_row:
        raise Unauthorized('Invalid API key')

    return uuid.UUID(user_row[0])


async def login(username: str, password: str) -> uuid.UUID:
    """Login a given user. Returns their user ID."""
    if not username or not password:
        raise Unauthorized('no username or password provided')

    user = await app.db.fetchrow("""
    select id, password_hash
    from users
    where username = ?
    """, username)

    if not user:
        raise Unauthorized('user not found')

    await check_password(password, user[1])
    return user[0]
