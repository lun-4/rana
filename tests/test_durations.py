import time
import pytest

@pytest.mark.asyncio
async def test_heartbeats(test_cli_user):
    resp = await test_cli_user.post('/api/v1/users/current/heartbeats', json={
        'entity': '/home/uwu/uwu.py',
        'type': 'file',
        'category': None,
        'time': time.time(),
        'project': 'awoo',
    })

    assert resp.status_code == 201
    rjson = await resp.json
    assert isinstance(rjson, dict)

    data = rjson['data']
    assert isinstance(data, dict)
    assert data['project'] == 'awoo'


@pytest.mark.asyncio
async def test_durations(test_cli_user):
    # TODO
    assert True
