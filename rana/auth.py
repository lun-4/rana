import asyncio

import bcrypt
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
