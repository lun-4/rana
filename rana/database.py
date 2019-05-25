import datetime
import logging
import uuid
import asyncio
from typing import Optional

import asyncpg

log = logging.getLogger()


def timestamp_(tstamp: Optional[int]) -> Optional[str]:
    """Return a ISO timestamp string from a UNIX timestamp integer."""
    if tstamp is None:
        return None

    dtm = datetime.datetime.fromtimestamp(tstamp)
    return dtm.isoformat()


def uuid_(identifier: Optional[str]) -> Optional[str]:
    """Return a json-friendly version of a given UUID string."""
    if identifier is None:
        return None

    return str(uuid.UUID(identifier))


SQL_SETUP_SCRIPT = """
create table if not exists users (
    id uuid primary key,
    username text unique not null,
    password_hash text not null,
    timezone text not null default 'Etc/GMT0',

    display_name text default null,
    website text default null,

    created_at bigint not null,
    modified_at bigint default null,

    languages_used_public bool default false not null,
    logged_time_public bool default false not null,

    last_heartbeat_at bigint default null,
    last_plugin text default null,
    last_plugin_name text default null,
    last_project text default null
);

create table if not exists api_keys (
    user_id uuid primary key references users (id),
    key text not null
);

create table if not exists machines (
    id uuid primary key,
    user_id uuid references users (id),
    name text
);

create table if not exists heartbeats (
    id uuid primary key,
    user_id uuid references users (id),
    machine_id uuid references machines (id),

    entity text not null,
    type text not null,
    category text default null,
    time real not null,
    is_write bool not null default false,

    project text default null,
    branch text default null,
    language text default null,
    lines bigint not null,
    lineno bigint default null,
    cursorpos bigint default null
);
"""


class Database:
    """Main database class."""
    def __init__(self, app):
        self.app = app
        asyncio.ensure_future(self.init(app))

    async def init(self, app):
        """Create basic tables."""
        self.conn = await asyncpg.create_pool(**dict(app.cfg['rana:database']))
        app.conn = self.conn
        await self.conn.execute(SQL_SETUP_SCRIPT)

    async def close(self):
        """Close the database."""
        log.debug('closing db')
        await self.conn.close()

    async def fetch(self, query, *args):
        """Execute a query and return the list of rows."""
        return await self.conn.fetch(query, *args)

    async def fetchrow(self, query, *args):
        """Execute a query and return a single result row."""
        return await self.conn.fetchrow(query, *args)

    async def fetchval(self, query, *args):
        """Execute a query and return the first value of the row."""
        return await self.conn.fetchval(query, *args)

    async def execute(self, query, *args):
        """Execute SQL."""
        return await self.conn.execute(query, *args)

    async def fetch_user_tz(self, user_id: uuid.UUID) -> Optional[str]:
        """Fetch a user's configured timezone."""
        return await self.fetchval(
            'select timezone from users where id = $1', user_id)

    async def fetch_user(self, user_id: uuid.UUID) -> Optional[dict]:
        """Fetch a single user and return the dictionary
        representing the API view of them.
        """
        row = await self.fetchrow("""
        select
            id, username, display_name, website, created_at, modified_at,
            last_heartbeat_at, last_plugin, last_plugin_name, last_project,
            timezone
        from users where id = $1
        """, user_id)

        if not row:
            return None

        user = {
            'id': uuid_(row[0]),
            'username': row[1],

            # no "full legal names" here uwuwuwuwu
            # trans rights
            'display_name': row[2],
            'full_name': row[2],

            'website': row[3],
            'created_at': timestamp_(row[4]),
            'modified_at': timestamp_(row[5]),

            'last_heartbeat_at': row[6],
            'last_plugin': row[7],
            'last_plugin_name': row[8],
            'last_project': row[9],
            'timezone': row[10],

            'logged_time_public': False,
            'languages_used_public': False,

            # i do not store full name or email pls
            'email': 'uwu@uwu.com',
            'email_public': False,

            # TODO: should we put something here?
            'photo': None,

            'is_hireable': False,
            'has_premium_features': False,
            'plan': 'basic',
            'location': 'Canberra, Australia',
        }

        if user['website'] is not None:
            # TODO: use urllib.parse
            user['human_readable_website'] = user['website'].lstrip('https://')

        return user

    async def fetch_user_simple(self, user_id: uuid.UUID) -> Optional[dict]:
        """Fetch a single simple view user."""
        row = await self.fetchrow("""
        select
            id, username, display_name, website
        from users where id = $1
        """, user_id)

        if not row:
            return None

        return {
            'id': uuid_(row[0]),
            'username': row[1],
            'display_name': row[2],
            'website': row[3],
        }

    async def fetch_heartbeat(self, heartbeat_id: uuid.UUID) -> Optional[dict]:
        """Fetch a single heartbeat."""
        # TODO: complete this query with all columns from heartbeats table.
        row = await self.fetchrow("""
        select
            id, entity, type, category, time, project, language
        from heartbeats where id = $1
        """, heartbeat_id)

        if not row:
            return None

        heartbeat = {
            'id': uuid_(row[0]),
            'entity': row[1],
            'type': row[2],
            'category': row[3],
            'time': row[4],
            'project': row[5],
            'language': row[6],
        }

        return heartbeat

    async def fetch_heartbeat_simple(
            self, heartbeat_id: uuid.UUID) -> Optional[dict]:
        """Fetch a single heartbeat."""
        row = await self.fetchrow("""
        select
            id, entity, type, time, project
        from heartbeats where id = $1
        """, heartbeat_id)

        if not row:
            return None

        heartbeat = {
            'id': uuid_(row[0]),
            'entity': row[1],
            'type': row[2],
            'time': row[3],
            'project': row[4],
        }

        return heartbeat
